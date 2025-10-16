import json
import boto3
import os


boto3_client = boto3.client('glue')


def workflow_is_running(name: str) -> bool:
    # Check recent runs; if any is RUNNING/WAITING, treat as busy
    resp = boto3_client.get_workflow_runs(Name=name, MaxResults=5)
    for r in resp.get("Runs", []):
        if r.get("Status") in ("RUNNING", "WAITING", "STOPPING"):
            return True
    return False


def myglueworkflow():
    WORKFLOW_NAME = os.environ["GLUE_WORKFLOW_NAME"]
    #WORKFLOW_NAME = 'hudi_to_silver_shreyash'
    response = None
    run_id = None

    try:
        if not workflow_is_running(WORKFLOW_NAME):
            response = boto3_client.start_workflow_run(
                Name=WORKFLOW_NAME,
            )
            if isinstance(response, dict):
                run_id = response.get("RunId")

            status = {
                'Job name': WORKFLOW_NAME,
                'Runid': run_id,
                'triggerby': 'lambda',
                'status': 'success'
            }
            return status
        else:
            status = {
                'Job name': WORKFLOW_NAME,
                'Runid': run_id,
                'triggerby': 'lambda',
                'status': 'cannot start',
                'reason': 'Another workflow is Running'
            }
            return status
    except Exception as e:
        status = {
            'Job name': WORKFLOW_NAME,
            'Runid': run_id,
            'triggerby': 'lambda',
            'status': "Error:" + str(e)
        }
        return status
    ...


def lambda_handler(event, context):
    status = myglueworkflow()
    print("Result :", status)
    return {
        'statusCode': 200,
        'body': json.dumps(status)
    }


