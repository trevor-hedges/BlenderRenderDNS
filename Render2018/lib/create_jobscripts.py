def create_mox_slurm(slurm_dir, slurm_name, job_name, lib_dir, python_file_to_run, case_config_path, render_config_path):
    """
    Creates slurm file that can be used to run a particular rendering script job on Mox.
    :param slurm_dir: Directory in which to save jobscript
    :param slurm_name: Name of jobscript
    :param job_name: Name of job
    :param lib_dir: Directory from which rendering scripts are run (lib directory).
    :param case_config_path: Directory to case config file to use
    :param render_config_path: Directory to render config file to use
    """
    with open(slurm_dir + "/" + slurm_name, "w") as jobscript:
        jobscript.write("#!/bin/bash\n")
        jobscript.write("#SBATCH --job-name=" + job_name + "\n")
        jobscript.write("#SBATCH --nodes=1\n")  # Won't need more than 1 node for rendering jobs... yet?
        jobscript.write("#SBATCH --time=24:00:00\n")  # Script run time shouldn't ever get close to 24h
        jobscript.write("#SBATCH --mem=50G\n")
        jobscript.write("#SBATCH --workdir=" + lib_dir + "\n")
        jobscript.write("export PATH=$PATH:/gscratch/ferrante/blender/blender-2.78c-linux-glibc219-x86_64/\n")  # Add Blender directory
        jobscript.write("python " + python_file_to_run + " -c " + case_config_path + " -r " + render_config_path + "\n")

    print("Created jobscript: " + slurm_dir)

def create_local_py(python_dir, python_filename, lib_dir, python_file_to_run, case_config_path, render_config_path):
    """
    Creates Python file that can be used to run a rendering job locally (not on Mox).
    :param python_dir: Directory in which to save .py file
    :param python_filename: .py filename
    :param lib_dir: Directory from which rendering scripts are run (lib directory).
    :param case_config_path: Directory to case config file to use
    :param render_config_path: Directory to render config file to use
    """
    with open(python_dir + "/" + python_filename, "w") as python_file:
        python_file.write("import os\n")
        python_file.write("os.chdir(\"" + lib_dir + "\")\n")
        python_file.write("os.system(\"python3 " + lib_dir + "/" + python_file_to_run + " -c " + case_config_path + " -r " + render_config_path + "\")")
