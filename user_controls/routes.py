from user_controls.Router import Router, DataStrategyEnum
from views.system_page import system_page
from views.software_page import software_page
from views.sam_page import sam_page
from views.NTUSER_page import ntuser_page

router = Router(DataStrategyEnum.QUERY)

router.routes = {
  "/": system_page,
  "/software_page": software_page,
  "/sam_page": sam_page,
  "/ntuser_page": ntuser_page
}
