import os
import asyncio
from typing import Any, Dict, List, Optional, Tuple
from scrapli.driver.core import AsyncIOSXEDriver
from rich import print as rprint
from inventory import DEVICES

username = os.environ["USERNAME"]
password = os.environ["PASSWORD"]

CLEAR = "clear"
os.system(CLEAR)
target = input("Please type the MAC address you're trying to locate: ")


def test_interfaces(interfaces: List[Dict[str, Any]]) -> Optional[str]:

    for interface in interfaces:
        try:
            mac_addr = interface["bia"]
            if target == mac_addr:
                return interface["interface"]
        except KeyError:
            pass
    return None


async def get_dev_info(device: Dict[str, str]) -> Tuple[str, List[Dict[str, Any]]]:

    hostname = device["hostname"]
    async with AsyncIOSXEDriver(
        host=device["host"],
        auth_username=username,
        auth_password=password,
        auth_strict_key=False,
        transport="asyncssh",
    ) as conn:
        intf_result = await conn.send_command("show interfaces")
        interfaces = intf_result.textfsm_parse_output()
        return hostname, interfaces


async def main() -> None:

    hit_found = False
    coroutines = [get_dev_info(device) for device in DEVICES]
    results = await asyncio.gather(*coroutines)
    for result in results:
        interface = test_interfaces(result[1])
        if interface is not None:
            hit_found = True
            rprint(
                f"""\n[green]Target {target} Found[/green]\n"""
                f"""{result[0]}: {interface}\n"""
            )
    if not hit_found:
        rprint(f"[red]\nTarget {target} Not Found[/red]\n")


asyncio.run(main())
