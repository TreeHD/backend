import json
from sqlalchemy.orm import Session

from app.db.models.port import Port
from app.db.models.port_forward import MethodEnum
from app.utils.v2ray import generate_v2ray_config

from tasks.functions.base import AppConfig


class V2rayConfig(AppConfig):
    method = MethodEnum.V2RAY

    def __init__(self):
        super().__init__()

        self.app_name = "v2ray"
        self.app_path = "/usr/local/bin/"

        self.app_get_role_name = "v2ray_get"
        self.app_sync_role_name = "v2ray_sync"

        self.traffic_meter = True
        self.update_status = True

    def apply(self, db: Session, port: Port):
        self.local_port = port.num

        v2ray_config = generate_v2ray_config(port.forward_rule)
        with open(f"ansible/project/roles/app/files/v2ray-{port.id}", "w") as f:
            f.write(json.dumps(v2ray_config, indent=2))
        if not (core := port.forward_rule.config.get("core", "v2ray")):
            core = "v2ray"
        self.app_command = (
            f"/usr/local/bin/{core} "
            f"{'-format=json' if core == 'xray' else ''} "
            f"-config /usr/local/etc/aurora/{port.num}"
        )
        self.app_config = f"v2ray-{port.id}"

        self.update_app = not port.server.config.get("v2ray")
        self.applied = True
        return self

    @property
    def playbook(self):
        return "app.yml"
