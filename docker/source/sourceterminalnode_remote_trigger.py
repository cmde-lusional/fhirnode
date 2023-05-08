import subprocess
import re

# Run the command and receive information of every containers cmd
def run_command(command):
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}")
        return ""

# uses the run_command method to execute each command and print it out on the docker host cmd
def execute_scripts(container_name):
    ## first three script are handled normally
    script_names = [
        "import_foreign_schema.py",
        "generate_fhir_json.py",
        "anonymize_fhir_json.py",
    ]

    for script in script_names:
        command = f"docker exec {container_name} python3 /init/{script}"
        print(f"Executing {script} in container {container_name}")
        output = run_command(command)
        print(output)

    ## for the flask script we need to run the process in the background to prevent outputting information to the
    ## cmd and stopping further execution of this script
    ## info can still be executed under: "docker logs fhirterminalnode_sourceterminalnode_x"
    # Execute the Flask script in the background
    flask_script = "export_fhir_json.py"
    command = f"docker exec -d {container_name} python3 /init/{flask_script}"
    print(f"Executing {flask_script} in container {container_name} (background)")
    subprocess.Popen(command, shell=True)


def main():
    docker_ps_output = run_command("docker ps --format '{{.Names}}'")
    container_name_pattern = re.compile(r'fhirterminalnode_sourceterminalnode_\d+')

    for line in docker_ps_output.splitlines():
        if container_name_pattern.match(line):
            execute_scripts(line)

if __name__ == '__main__':
    main()
