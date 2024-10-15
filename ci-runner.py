#!/usr/bin/env python
import os
import yaml
import shutil
import subprocess
import argparse
import logging
from dotenv import load_dotenv


# Check wether required environment varibles has been set on .env, otherwise fail quickly.
required_dotenv_vars = [
    'CLUSTER_NAME', 'BASE_DOMAIN',
    'LEASED_RESOURCE', 'JOB_NAME',
    'PULL_SECRET_FILE', 'RELEASE_REPO_PATH',
    'SSH_PUBLIC_KEY']
SKIP_STEPS=[]

VOLUME_HOST_PATH = os.getenv("VOLUME_HOST_PATH",os.path.dirname(os.path.realpath(__file__))+"/volumes")
WORKDIR_HOST_PATH = os.getenv("WORKDIR_HOST_PATH",os.path.dirname(os.path.realpath(__file__))+"/volumes/__runtime__")
os.environ['VOLUME_HOST_PATH'] = VOLUME_HOST_PATH
os.environ['WORKDIR_HOST_PATH'] = WORKDIR_HOST_PATH

def get_env_or_die(name):
    val = os.getenv(name)
    if val == None:
        raise Exception("environment variable: ", name, " is required but not defined")        
    return val

def load_env_vars():
    """
    Check required environment variables and load it from .env.
    """
    # Load environment from .env
    load_dotenv()

    # Check if required variables has been set in .env
    errors = []
    for key in required_dotenv_vars:
        if key not in os.environ:
            errors.append(key)
        if len(errors) > 0:
            raise Exception("Missing required environment variables: " + ', '.join(errors))

    # Load default environment variables
    print("Setting up environment variables")

    # TODO(mtulio): move to a better place

    default_env_vars = {
        'BUILD_ID': '000',
        'UNIQUE_HASH': 'abc',
        'LEASED_RESOURCE': get_env_or_die('LEASED_RESOURCE'),
        'JOB_NAME': get_env_or_die('JOB_NAME'),
        'CI_WORKDIR': f'/tmp/{ get_env_or_die("CLUSTER_NAME") }',
        'SHARED_DIR': f'{ WORKDIR_HOST_PATH }/shared',
        'ARTIFACT_DIR': f'{ WORKDIR_HOST_PATH }/artifact',
        'PROFILE_DIR': f'{ VOLUME_HOST_PATH }/cluster-profile',
        'CLUSTER_PROFILE_DIR': f'{ VOLUME_HOST_PATH }/cluster-profile',
        'KUBECONFIG': f'{ os.getenv("SHARED_DIR")}/kubeconfig',
        'NAMESPACE': os.getenv('CLUSTER_NAME'),
        'OCP_ARCH':  os.getenv('CLUSTER_NAME', 'amd64'),
        'PERSISTENT_MONITORING':  os.getenv('PERSISTENT_MONITORING', 'false')
    }
    for key in default_env_vars:
        try:
            if key == 'SKIP_STEPS':
                SKIP_STEPS = os.getenv('SKIP_STEPS').split(',')
                print(f"Setting key={key} value={SKIP_STEPS}")
                continue
            print(f"Setting key={key} value={default_env_vars[key]}")
            os.environ[key] = default_env_vars[key]
        except Exception as e:
            logging.error(f"Error setting environment variable {key}: {e}")
    print(os.getenv("ARTIFACT_DIR"))
def load_env_ref(envs):
    """
    Set default environment variables from ref (step) definition.
    """
    print("Setting up environment variables for ref")
    loaded_vars = []
    for env_def in envs:
        try:
            # this allow override of env vars from ref
            if env_def['name'] not in os.environ:
                logging.debug(f"Setting default env value from Ref definition: key={env_def['name']} value={env_def['default']}")
                loaded_vars.append(env_def['name'])
                os.environ[env_def['name']] = env_def['default']
        except Exception as e:
            logging.error(f"Error setting environment variable {env_def['name']}: {e}")

    return loaded_vars

def unload_vars(vars):
    """
    Unload environment variables loaded from ref (step) definition.
    """
    for var in vars:
        if var in os.environ:
                del os.environ[var]

def initialize():
    """
    Initialize the local directories to prepare for running steps.
    """
    print("Initializing")

    if os.path.exists(WORKDIR_HOST_PATH):
        shutil.rmtree(WORKDIR_HOST_PATH)

    if os.path.exists(os.getenv('CI_WORKDIR')):
        shutil.rmtree(os.getenv('CI_WORKDIR'))
    
    if os.path.exists(f'/tmp/install-dir'):
        shutil.rmtree('/tmp/install-dir')

    print("Setting up required artifacts")
    os.makedirs(os.getenv('CI_WORKDIR'), exist_ok=True)
    os.makedirs(os.getenv('SHARED_DIR'), exist_ok=True)
    os.makedirs(os.getenv('PROFILE_DIR'), exist_ok=True)
    os.makedirs(os.getenv('ARTIFACT_DIR'), exist_ok=True)
    shutil.copyfile(os.getenv('SSH_PRIVATE_KEY'), f'{os.getenv("PROFILE_DIR")}/ssh-private')
    shutil.copyfile(os.getenv('SSH_PUBLIC_KEY'), f'{os.getenv("PROFILE_DIR")}/ssh-publickey')
    shutil.copyfile(os.getenv('PULL_SECRET_FILE'), f'{os.getenv("PROFILE_DIR")}/pull-secret')
    shutil.copyfile(os.getenv('AWS_CREDENTIAL_PATH'), f'{os.getenv("PROFILE_DIR")}/.awscred')

def scan_dir_for(type, path, name, pathParts=""):
    """
    Walkthough the local release repository to manifest definition for each CI step.
    """
    try:
        if '.git/' in path:
            return

        if os.path.isfile(path):
            filename = os.path.basename(path)
            if filename == name + "-" + type + ".yaml":
                return path
            else:
                return

        for filename in os.listdir(path):
            if os.path.isfile(filename):
                pass
            if pathParts != "":
                thisPath = filename
            else:
                thisPath = "-" + filename
            foundPath = scan_dir_for(type, path + "/" + filename, name, thisPath)
            if foundPath != None:
                return foundPath
    except Exception as e:
        logging.error(f"Error scanning directory for {type}: path={path} name={name}:\n {e}")
        raise e

def runInPodman(ref):        
    release_path = os.getenv('RELEASE_REPO_PATH')
    podmanArgs = ["podman", "run"]
    if "credentials" in ref:
        for credential in ref["credentials"]:
            volume_name = credential["name"]
            volume_path = os.path.join(VOLUME_HOST_PATH, volume_name)
            if os.path.isdir(volume_path) == False:
                print("!!! volume ", volume_name, " not found. will not mount the secret.")
                continue
            podmanArgs.append("-v")
            podmanArgs.append(volume_path+":"+credential["mount_path"]+":z")

    podmanArgs.append("-v")
    podmanArgs.append(release_path+":"+release_path+":z")

    podmanArgs.append("-v")
    podmanArgs.append(os.path.join(VOLUME_HOST_PATH,"cluster-profile")+":/var/run/secrets/ci.openshift.io/cluster-profile:z")

    podmanArgs.append("-v")
    print("volume path: ", os.path.join(VOLUME_HOST_PATH,"__runtime__"))    
    podmanArgs.append(VOLUME_HOST_PATH+":/usr/app/src/volumes:z")

    podmanArgs.append("-a")
    podmanArgs.append("STDERR")

    podmanArgs.append("-a")
    podmanArgs.append("STDOUT")

    if "from" in ref:
        print("image: ", ref["from"])
        podmanArgs.append(ref["from"] + ":latest")
    else:
        raise Exception("image not found. add \"from\" to the step and refer to a compatible local image.")
    
    podmanArgs.append('python')
    podmanArgs.append('/usr/app/src/ci-runner.py')
    podmanArgs.append('--run-step')
    podmanArgs.append(ref["as"])
    
    print('podman command: ',' '.join([str(x) for x in podmanArgs]))
    result = subprocess.run(podmanArgs, capture_output=True, env=os.environ)
    print(result.stdout.decode())
    print(result.stderr.decode())
    print("container exit code: ", result.returncode)

    if result.returncode != 0:
        exit(result.returncode)

def processRef(ref, invoke_scripts=True, run_in_image=False):
    global path
    
    refPath = scan_dir_for("ref", os.getenv('RELEASE_REPO_PATH'), ref)
    if refPath == None:
        print("ref[" + ref + "] not found")
        return 1
    with open(refPath, "r") as stream:
        try:
            ref = yaml.safe_load(stream)            
            ref = ref["ref"]
            shPath = os.path.dirname(refPath) + "/" + ref["commands"]
            print("ref:["+ref["as"]+"]----> " + shPath)
            for job in SKIP_STEPS:
                if job in ref["as"]:
                    print("skipping ref")
                    return 0
            # Load default env vars from ref when is defined
            loaded_step_vars = []
            loaded_step_vars.clear()
            if 'env' in ref:
                loaded_step_vars = load_env_ref(ref["env"])
            
            if run_in_image:
                runInPodman(ref)                
            elif invoke_scripts:
                result = -1
                if shPath.endswith(".py"):
                    result = subprocess.run(["python" , shPath], capture_output=True, env=os.environ)
                    print(result.stdout.decode())
                    print(result.stderr.decode())
                else:
                    print("starting ", shPath)
                    result = subprocess.run(["bash" , shPath], capture_output=True, env=os.environ)
                    print(result.stdout.decode())
                    print(result.stderr.decode())
                    
                print("exit code: ", result.returncode)
                exit(result.returncode)                
            else:
                if "from" in ref:
                    print("image: ", ref["from"])
                if "credentials" in ref:
                    for credential in ref["credentials"]:
                        print("volume: ", credential["name"])

        except yaml.YAMLError as exc:
            print(exc)
    return 0

def processChain(chain, invoke_scripts=True, run_in_image=False):
    global path
    chainPath = scan_dir_for("chain", os.getenv('RELEASE_REPO_PATH'), chain)
    if chainPath == None:
        print("chain[" + chain + "] not found")
        return 1
    with open(chainPath, "r") as stream:
        try:
            chain = yaml.safe_load(stream)            
            if "chain" not in chain:
                print("yaml is not a chain")
                return
            chain = chain["chain"]
            steps = chain["steps"]
            for step in steps:
                if "ref" in step:                    
                    if processRef(step["ref"], invoke_scripts=invoke_scripts, run_in_image=run_in_image) != 0:
                        raise Exception("step failed")
                if "chain" in step:
                    print("chain:["+chain["as"]+"]-->")
                    processChain(step["chain"], invoke_scripts=invoke_scripts, run_in_image=run_in_image)
                    
        except yaml.YAMLError as exc:
            print(exc)
    return 1            

def processWorkflow(workflow, invoke_scripts=True, run_in_image=True):
    global path

    workflowPath = scan_dir_for("workflow", os.getenv('RELEASE_REPO_PATH'), workflow)
    if workflowPath == None:
        print("workflow[" + workflow + "] not found")
        return
    with open(workflowPath, "r") as stream:
        try:
            workflow = yaml.safe_load(stream)            
            if "workflow" not in workflow:
                raise Exception("yaml is not a workflow")
                
            workflow = workflow["workflow"]
            steps = workflow["steps"]
            stepTypes = ["pre", "test", "post"]
            for stepType in stepTypes:                
                if stepType in steps:
                    print("workflow["+workflow["as"]+"] phase["+stepType+"]")
                    preSteps = steps[stepType]
                    for step in preSteps:    
                        if "ref" in step:
                            if processRef(step["ref"], invoke_scripts=invoke_scripts, run_in_image=run_in_image) != 0 and stepType == "pre":
                                raise Exception("step failed. exiting 'pre' chain")
                                break
                        elif "chain" in step:                            
                            if processChain(step["chain"], invoke_scripts=invoke_scripts, run_in_image=run_in_image) !=0 and stepType == "pre":
                                raise Exception("chain failed. exiting 'pre' chain")
                                break
                        else:
                            raise Exception("unrecognized step class - " + step)
                    
        except yaml.YAMLError as exc:
            raise Exception(exc)

def discoverMountPaths(workflow):
    pass

def main():
    load_env_vars()

    # Set up the argument parser
    parser = argparse.ArgumentParser(description="A CLI tool for executing CI operator artifacts")
    
    # Define the arguments
    parser.add_argument('--run-chain', type=str, help='Run the specified chain')
    parser.add_argument('--run-step', type=str, help='Run the specified step')    
    parser.add_argument('--run-in-image', action='store_true', help='Run the step in an image associated with the step')
    parser.add_argument('--run-workflow', type=str, help='Run the specified workflow')
    parser.add_argument('--print-workflow', type=str, help='Prints images and volumes required by a workflow')
    parser.add_argument('--initialize', '--init', action='store_true', help='Initializes local directories to prepare for running artifacts')
    
    # Parse the arguments
    args = parser.parse_args()

    if args.initialize:
        initialize()

    # Perform the appropriate actions based on the arguments
    if args.run_workflow:
        processWorkflow(args.run_workflow, run_in_image=args.run_in_image)
    elif args.print_workflow:
        processWorkflow(args.print_workflow, invoke_scripts=False)        
    elif args.run_chain:
        processChain(args.run_chain, run_in_image=args.run_in_image)
    elif args.run_step:
        processRef(args.run_step, run_in_image=args.run_in_image)
if __name__ == "__main__":
    main()
