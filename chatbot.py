import json
import sagemaker
import boto3
from sagemaker.huggingface import HuggingFaceModel, get_huggingface_llm_image_uri

try:
	role = sagemaker.get_execution_role()
except ValueError:
	iam = boto3.client('iam')
	role = iam.get_role(RoleName='sagemaker_execution_role')['Role']['Arn']

# Hub Model configuration. https://huggingface.co/models
hub = {
	'HF_MODEL_ID':'tiiuae/falcon-180B-chat',
	'SM_NUM_GPUS': json.dumps(8),
	'HUGGING_FACE_HUB_TOKEN': '<REPLACE WITH YOUR TOKEN>'
}

assert hub['HUGGING_FACE_HUB_TOKEN'] != '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', "You have to provide a token."

# create Hugging Face Model Class
huggingface_model = HuggingFaceModel(
	image_uri=get_huggingface_llm_image_uri("huggingface",version="1.1.0"),
	env=hub,
	role=role, 
)

# deploy model to SageMaker Inference
predictor = huggingface_model.deploy(
	initial_instance_count=1,
	instance_type="ml.p4de.24xlarge",
	container_startup_health_check_timeout=300,
  )
  
# send request
predictor.predict({
	"inputs": "My name is Julien and I like to",
})