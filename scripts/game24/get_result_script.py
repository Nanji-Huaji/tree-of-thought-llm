import subprocess


base_command = [
    "--task", "game24",
    "--task_start_index", "900",
    "--task_end_index", "909",
    "--method_generate", "propose",
    "--method_evaluate", "value",
    "--method_select", "greedy",
    "--n_evaluate_sample", "3",
    "--n_select_sample", "5",
    "--temperature", "0.9",
    "--localbackend", "phi-3.1-mini-128k-instruct",
]
add_command = [
    "--slm_generate",
    "--check_format",
    "--eval_rule",
    "--slm_eval",
    "--warm_start"]

python_command_res = [
    "python", "results/get_results.py",
]

command_list = [
    python_command_res + base_command + ["--slm_generate", "--slm_eval", "--check_format","--eval_rule"],
    python_command_res + base_command + ["--slm_generate", "--slm_eval", "--check_format","--eval_rule","--last_lm"],
    python_command_res + base_command + ["--slm_generate", "--check_format","--eval_rule","--last_lm"],
    python_command_res + base_command + ["--slm_eval", "--check_format","--eval_rule"],
    python_command_res + base_command + ["--check_format","--eval_rule"],
    python_command_res + base_command + ["--filter","--last_lm"]
]

# Loop --inference_idx from 0-2
for command in command_list:
    cur_command = command
    print(f"Running command: {' '.join(cur_command)}")
    try:
        subprocess.run(cur_command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
