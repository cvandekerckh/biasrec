import random as rd 
import pandas as pd
from config import Config as Cf

CONDITION_FILENAME = 'conditions.csv'
USER_FILENAME = 'users.csv'
USER_CONDITION_FILENAME = 'users_conditions.csv'
USER_CONDITION_DETAILED_FILENAME = 'users_conditions_detailed.csv'


def between_subject_experiment(user_list, condition_list):
    """
    Allocate users randomly and evenly among conditions in a between-subject experiment design.
    
    Args:
    - user_list (list): List of users
    - condition_list (list): List of experimental conditions
    
    Returns:
    - experiment_design (dict): Dictionary mapping users to their assigned conditions
    """
    # Shuffle the user list to randomize assignment
    rd.seed(0)
    rd.shuffle(user_list)
    
    # Calculate the number of users per condition
    users_per_condition = len(user_list) // len(condition_list)
    
    # Initialize the experiment design dictionary
    experiment_design = {user: None for user in user_list}
    
    # Allocate users to conditions
    for i, condition in enumerate(condition_list):
        start_index = i * users_per_condition
        end_index = start_index + users_per_condition
        
        # Assign users to the current condition
        for user in user_list[start_index:end_index]:
            experiment_design[user] = condition
    
    # Assign remaining users if any
    remaining_users = len(user_list) % len(condition_list)
    if remaining_users:
        for i in range(remaining_users):
            user = user_list[-(i+1)]  # Assign remaining users from the end of the list
            experiment_design[user] = condition_list[i]
    
    return experiment_design


def assign_conditions():
    df_condition = pd.read_csv(Cf.DATA_PATH_RAW / CONDITION_FILENAME)
    df_user = pd.read_csv(Cf.DATA_PATH_RAW /USER_FILENAME, delimiter=';')
    assert df_user.shape[0] >= df_condition.shape[0]  # assert we have more users than conditions
    user_list = df_user["id"].values.tolist()
    condition_list = df_condition["condition_id"]
    experiment_design = between_subject_experiment(user_list, condition_list)

    df_user['condition_id'] = df_user["id"].map(experiment_design)
    df_user.to_csv(Cf.DATA_PATH_OUT / USER_CONDITION_FILENAME, index=False)
