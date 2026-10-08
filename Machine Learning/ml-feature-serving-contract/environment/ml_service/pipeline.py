from .inference import predict_file
def predict(path,artifact_path="/app/data/model_artifact.json"):
    return predict_file(path,artifact_path)
