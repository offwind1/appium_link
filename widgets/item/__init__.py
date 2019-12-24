from .action_clickItem import Action_ClickItem
from .action_sendKeyItem import Action_SendKeyItem
from .action_send_key_event_item import Action_Send_Key_Event_Item
from .action_swip_item import Action_Swip_Item
from .action_wait_item import Action_Wait_Item

from .logic_forItem import Logic_ForItem
from .logic_include_item import Logic_Include_Item
from .logic_execute_item import Logic_Execute_Item

from .value_setPartValueItem import Value_setPartValueItem
from .value_setGlobalValueItem import Value_setGlobalValueItem
from .value_getValue_item import Value_GetValue_Item
from .value_valueCal_item import Value_ValueCal_Item


from .mainTitleItem import MainTitleItem
from .mainSuiteItem import MainSuiteItem
from .baseItem import *

ITEM_LIST = [
    {"动作":[Action_ClickItem,
            Action_SendKeyItem,
            Action_Send_Key_Event_Item,
            Action_Wait_Item,
            Action_Swip_Item]},
    {"逻辑":[Logic_ForItem, 
            Logic_Include_Item]},
    {"变量":[Value_setPartValueItem,
            Value_setGlobalValueItem,
            Value_GetValue_Item,
            Value_ValueCal_Item]}
]

SUITE_LIST = [
        {"逻辑":[Logic_Execute_Item]}
]

KEY_DICT = {"click":Action_ClickItem,
        "sendkey":Action_SendKeyItem,
        "send_event":Action_Send_Key_Event_Item,
        "wait":Action_Wait_Item,
        "logic_for":Logic_ForItem,
        "swip":Action_Swip_Item,
        "include":Logic_Include_Item,
        "execute":Logic_Execute_Item,
        "main":MainTitleItem,
        "suite":MainSuiteItem,
        "value_part":Value_setPartValueItem,
        "value_get":Value_GetValue_Item,
        "value_cal":Value_ValueCal_Item,
        "value_global":Value_setGlobalValueItem
}