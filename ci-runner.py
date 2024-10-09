#!/usr/bin/python
import os
import yaml
import shutil
import subprocess
import argparse
import env

env_vars = {
    'PULL_SECRET_FILE': env.PULL_SECRET_FILE,
    'CLUSTER_NAME': f'{env.CLUSTER_NAME}',
    'SHARED_DIR': env.SHARED_DIR,
    'ARTIFACT_DIR': env.ARTIFACT_DIR,
    'PROFILE_DIR': env.PROFILE_DIR,
    'CLUSTER_PROFILE_DIR': env.PROFILE_DIR,
    'PLATFORM_EXTERNAL_CCM_ENABLED': 'yes',
    'PROVIDER_NAME': env.PROVIDER_NAME,
    'BASE_DOMAIN': env.BASE_DOMAIN,
    'JOB_NAME': env.JOB_NAME,
    'BUILD_ID': '000',
    'AWS_REGION': env.AWS_REGION,
    'LEASED_RESOURCE': env.AWS_REGION,
    'BOOTSTRAP_INSTANCE_TYPE': 'm5.xlarge',
    'MASTER_INSTANCE_TYPE': 'm5.xlarge',
    'WORKER_INSTANCE_TYPE': 'm5.xlarge',
    'OCP_ARCH': 'amd64',
    'TELEMETRY_ENABLED': 'true',
    'NAMESPACE': env.CLUSTER_NAME,
    'PERSISTENT_MONITORING': 'false',
    'OPENSHIFT_INSTALL_RELEASE_IMAGE_OVERRIDE': env.RELEASE_IMAGE,
    'RELEASE_IMAGE_LATEST': env.RELEASE_IMAGE,
    'UNIQUE_HASH': '12346',
    'FIPS_ENABLED': 'false',
    'BASELINE_CAPABILITY_SET': '',
    #'BASELINE_CAPABILITY_SET': 'None',
    # 'ADDITIONAL_ENABLED_CAPABILITIES': 'MachineAPI CloudCredential CloudControllerManager Ingress',
    'ADDITIONAL_ENABLED_CAPABILITIES': '',
    'PUBLISH': 'External',
    'FEATURE_SET': '',
    'FEATURE_GATES': '',
    'MACHINE_CIDR': env.MACHINE_CIDR,
    'CCM_NAMESPACE': env.CCM_NAMESPACE
}

print("Setting up environment variables")
for key in env_vars:    
    os.environ[key] = env_vars[key]

def initialize():
    print("Initializing")
    if os.path.exists(f'/tmp/{env.CLUSTER_NAME}'):
        shutil.rmtree(f'/tmp/{env.CLUSTER_NAME}')
    
    if os.path.exists(f'/tmp/install-dir'):
        shutil.rmtree('/tmp/install-dir')

    print("Setting up required artifacts")
    os.mkdir(f'/tmp/{env.CLUSTER_NAME}')
    
    if not os.path.isdir(env.PROFILE_DIR):
        os.mkdir(env.PROFILE_DIR)
    
    os.mkdir(env.SHARED_DIR)
    os.mkdir(env.ARTIFACT_DIR)    
    shutil.copyfile(env.SSH_PUBLIC_KEY, f'{env.PROFILE_DIR}/ssh-publickey')
    shutil.copyfile(env.PULL_SECRET_FILE, f'{env.PROFILE_DIR}/pull-secret')
    shutil.copyfile(env.AWS_CREDENTIAL_PATH, f'{env.PROFILE_DIR}/.awscred')

def scan_dir_for(type, path, name, pathParts=""):        
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

def processRef(ref, invoke_scripts=True):
    global path
    refPath = scan_dir_for("ref", env.RELEASE_REPO_PATH, ref)
    if refPath == None:
        print("ref[" + ref + "] not found")
        return 1
    with open(refPath, "r") as stream:
        try:
            ref = yaml.safe_load(stream)            
            ref = ref["ref"]
            shPath = os.path.dirname(refPath) + "/" + ref["commands"]
            print("ref:["+ref["as"]+"]----> " + shPath)
            for job in env.skipSteps:
                if job in ref["as"]:
                    print("skipping ref")
                    return 0
            if invoke_scripts:
                result = -1
                if shPath.endswith(".py"):
                    result = subprocess.run(["python" , shPath])
                else :
                    result = subprocess.run(["bash" , shPath])
                return result.returncode
            else:
                if "credentials" in ref:
                    print(ref["credentials"])

        except yaml.YAMLError as exc:
            print(exc)
    return 0

def processChain(chain):
    global path
    chainPath = scan_dir_for("chain", env.RELEASE_REPO_PATH, chain)
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
                    if processRef(step["ref"]) != 0:
                        print("failed")
                        exit(1)                   
                if "chain" in step:
                    print("chain:["+chain["as"]+"]-->")
                    processChain(step["chain"])
                    
        except yaml.YAMLError as exc:
            print(exc)
    return 1            

def processWorkflow(workflow, invoke_scripts=True):
    global path
    initialize()
    workflowPath = scan_dir_for("workflow", env.RELEASE_REPO_PATH, workflow)
    if workflowPath == None:
        print("workflow[" + workflow + "] not found")
        return
    with open(workflowPath, "r") as stream:
        try:
            workflow = yaml.safe_load(stream)            
            if "workflow" not in workflow:
                print("yaml is not a workflow")
                return
            workflow = workflow["workflow"]
            steps = workflow["steps"]
            stepTypes = ["pre", "test", "post"]
            for stepType in stepTypes:                
                if stepType in steps:
                    print("workflow["+workflow["as"]+"] phase["+stepType+"]")
                    preSteps = steps[stepType]
                    for step in preSteps:    
                        if "ref" in step:
                            if processRef(step["ref"], invoke_scripts=invoke_scripts) != 0 and stepType == "pre":
                                print("step failed. exiting 'pre' chain")
                                break
                        elif "chain" in step:                            
                            if processChain(step["chain"]) !=0 and stepType == "pre":
                                print("chain failed. exiting 'pre' chain")
                                break
                        else:
                            print("unrecognized step class - " + step)
                    
        except yaml.YAMLError as exc:
            print(exc)

def discoverMountPaths(workflow):
    pass

def main():
    # Set up the argument parser
    parser = argparse.ArgumentParser(description="A CLI tool for executing CI operator artifacts")
    
    # Define the arguments
    parser.add_argument('--run-chain', type=str, help='Run the specified chain')
    parser.add_argument('--run-step', type=str, help='Run the specified step')
    parser.add_argument('--run-workflow', type=str, help='Run the specified workflow')
    parser.add_argument('--initialize', action='store_true', help='Initializes local directories to prepare for running artifacts')
    
    # Parse the arguments
    args = parser.parse_args()

    # Perform the appropriate actions based on the arguments
    if args.run_chain:
        processChain(args.run_chain)

    if args.run_step:
        processRef(args.run_step)

    if args.run_workflow:
        processWorkflow(args.run_workflow)

    if args.initialize:
        initialize()

if __name__ == "__main__":
    main()
