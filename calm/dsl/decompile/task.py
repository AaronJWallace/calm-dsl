import uuid

from calm.dsl.decompile.render import render_template
from calm.dsl.decompile.ref import render_ref_template
from calm.dsl.decompile.credential import get_cred_var_name
from calm.dsl.decompile.file_handler import get_scripts_dir
from calm.dsl.builtins import TaskType
from calm.dsl.builtins import RefType


def render_task_template(cls, RUNBOOK_ACTION_MAP={}):

    if not isinstance(cls, TaskType):
        raise TypeError("{} is not of type {}".format(cls, TaskType))

    user_attrs = cls.get_user_attrs()
    user_attrs["name"] = cls.__name__
    # sample for exec and ssh type task

    target = getattr(cls, "target_any_local_reference", None)
    if target:
        if not target.__name__.isidentifier():
            target.__name__ = "D{}".format(target.__name__)

        user_attrs["target"] = render_ref_template(target)

    cred = cls.attrs.get("login_credential_local_reference", None)
    if cred:
        user_attrs["cred"] = "ref({})".format(get_cred_var_name(cred["name"]))

    if cls.type == "EXEC":
        script_type = cls.attrs["script_type"]
        cls.attrs["script"] = cls.attrs["script"].replace("'", r"/'")
        cls.attrs["script"] = create_script_file(script_type, cls.attrs["script"])
        
        if script_type == "sh":
            schema_file = "task_exec_ssh.py.jinja2"

        elif script_type == "static":
            schema_file = "task_exec_escript.py.jinja2"

        elif script_type == "npsscript":
            schema_file = "task_exec_powershell.py.jinja2"

    elif cls.type == "SET_VARIABLE":
        variables = cls.attrs.get("eval_variables", None)
        if variables:
            user_attrs["variables"] = variables
        script_type = cls.attrs["script_type"]
        cls.attrs["script"] = cls.attrs["script"].replace("'", r"/'")
        if script_type == "sh":
            schema_file = "task_setvariable_ssh.py.jinja2"

        elif script_type == "static":
            schema_file = "task_setvariable_escript.py.jinja2"

        elif script_type == "npsscript":
            schema_file = "task_setvariable_powershell.py.jinja2"

    elif cls.type == "DELAY":
        if hasattr(cls, "attrs"):
            user_attrs["delay_seconds"] = cls.attrs.get("interval_secs", 0)
        schema_file = "task_delay.py.jinja2"

    elif cls.type == "SCALING":
        scaling_count = cls.attrs.get("scaling_count", 1)
        if scaling_count:
            user_attrs["scaling_count"] = scaling_count
        scaling_type = cls.attrs["scaling_type"]
        if scaling_type == "SCALEOUT":
            schema_file = "task_scaling_scaleout.py.jinja2"

        elif scaling_type == "SCALEIN":
            schema_file = "task_scaling_scalein.py.jinja2"
    elif cls.type == "HTTP":
        attrs = cls.attrs
        # TODO add basic_cred creds support. For now default cred used
        user_attrs["headers"] = {}
        user_attrs["secret_headers"] = {}
        user_attrs["status_mapping"] = {}

        for var in attrs.get("headers", []):
            var_type = var["type"]
            if var_type == "LOCAL":
                user_attrs["headers"][var["name"]] = var["value"]

            elif var_type == "SECRET":
                user_attrs["secret_headers"][var["name"]] = var["value"]

        for status in attrs.get("expected_response_params", []):
            user_attrs["status_mapping"][status["code"]] = (
                True if status["status"] == "SUCCESS" else False
            )

        user_attrs["response_paths"] = attrs.get("response_paths", {})
        method = attrs["method"]

        if method == "GET":
            schema_file = "task_http_get.py.jinja2"

        elif method == "POST":
            schema_file = "task_http_post.py.jinja2"

        elif method == "PUT":
            schema_file = "task_http_put.py.jinja2"

        elif method == "DELETE":
            # TODO remove it from here
            if not cls.attrs["request_body"]:
                cls.attrs["request_body"] = {}
            schema_file = "task_http_delete.py.jinja2"

    elif cls.type == "CALL_RUNBOOK":
        # TODO shift this working to explicit method for task decompile
        runbook = RefType.decompile(cls.attrs["runbook_reference"])
        runbook_target = cls.target_any_local_reference

        user_attrs = {
            "name": cls.__name__,
            "action": RUNBOOK_ACTION_MAP[runbook.__name__],
            "target": runbook_target.__name__
        }
        schema_file="task_call_runbook.py.jinja2"

    else:
        raise Exception("Invalid task type")

    text = render_template(schema_file=schema_file, obj=user_attrs)
    return text.strip()


def create_script_file(script_type, script=""):
    """create the script file and return the file location"""

    file_name = "task_file_{}".format(str(uuid.uuid4())[:8])
    scripts_dir = get_scripts_dir()

    if script_type == "sh":
        file_name += ".sh"
    
    elif script_type == "npsscript":
        file_name += ".ps1"
    
    elif script_type == "static":
        file_name += ".py"
    
    else:
        raise TypeError("Script Type {} not supported". format(script_type))

    with open("{}/{}".format(scripts_dir, file_name), "w+") as fd:
        fd.write(script)
    
    return "specs/{}".format(file_name)