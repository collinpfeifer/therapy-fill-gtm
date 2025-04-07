import yaml


def configuration():
    with open("auth.yaml", "r") as file:
        auth = yaml.safe_load(file)
    with open("config.yaml", "r") as file:
        config = yaml.safe_load(file)
    return auth, config
