from .types import t_scheduler
from .manager import Manager
import pretty_cron
import requests
import pycron


class Scheduler:
    naas = None
    role = t_scheduler

    def __init__(self):
        self.manager = Manager()
        self.get_output = self.manager.get_output
        self.clear_output = self.manager.clear_output
        self.list = self.manager.list_prod
        self.clear = self.manager.clear_prod
        self.get = self.manager.get_prod

    def status(self):
        req = requests.get(url=f"{self.manager.naas_api}/scheduler")
        req.raise_for_status()
        jsn = req.json()
        print(jsn)
        return jsn

    def pause(self):
        req = requests.get(url=f"{self.manager.naas_api}/scheduler/pause")
        req.raise_for_status()
        jsn = req.json()
        print(jsn)
        return jsn

    def resume(self):
        req = requests.get(url=f"{self.manager.naas_api}/scheduler/resume")
        req.raise_for_status()
        jsn = req.json()
        print(jsn)
        return jsn

    def currents(self, raw=False):
        json_data = self.manager.get_naas()
        if raw:
            for item in json_data:
                if item["type"] == self.role:
                    print(item)
        else:
            for item in json_data:
                kind = None
                if item["type"] == self.role:
                    cron_string = pretty_cron.prettify_cron(item["value"])
                    kind = f"scheduler {cron_string}"
                    print(f"File ==> {item['path']} is {kind}")

    def __check_cron(self, text):
        res = False
        try:
            pycron.is_now(text)
            res = True
        except ValueError:
            pass
        return res

    def add(self, path=None, recurrence=None, params={}, debug=False):
        if self.manager.is_production():
            print("No add done you are in production\n")
            return
        if not recurrence:
            print("No recurrence provided\n")
            return
        if not self.__check_cron(recurrence):
            print(f"WARNING : Recurrence wrong format {recurrence}")
            return
        current_file = self.manager.get_path(path)
        self.manager.add_prod(
            {
                "type": self.role,
                "path": current_file,
                "params": params,
                "value": recurrence,
            },
            debug,
        )
        cron_string = pretty_cron.prettify_cron(recurrence)
        print("👌 Well done! Your Notebook has been sent to production. \n")
        print(
            f'⏰ It will be scheduled "{cron_string}" (more on the syntax on https://crontab.guru/).\n'
        )
        print('Ps: to remove the "Scheduler", just replace .add by .delete')

    def delete(self, path=None, all=False, debug=False):
        if self.manager.is_production():
            print("No delete done you are in production\n")
            return
        current_file = self.manager.get_path(path)
        self.manager.del_prod({"type": self.role, "path": current_file}, debug)
        print("🗑 Done! Your Scheduler has been remove from production.\n")
        if all is True:
            self.clear(path)
            self.clear_output(path)
