přístupové api do cribisu

https://www.nylas.com/blog/use-python-requests-module-rest-apis/


ošetřit chybové hlášky z api
dostupnost přístupu adresy/služby cribis
neplatnost přihlašovacích údajů


převedení xml odpovědi do json objektu pak do pythonu

zapsání do odoo

modely

rozšíření res.partner
vazba na nové tabulky

cribis_microreport
tabulka všech reportů s vazbou na partner id v res.partner s vazbou many2one z cribis_microreport na res.partner.cribis_microreport_id

cribis_monitoring
res.partner.cribis_monitoring bool
tabulka všech monitoringů s vazbou na partner id v res.partner s vazbou many2one z cribis_monitoring na res.partner.cribis_monitoring_id

rozšíření res.company
buton pro ověření aktuálního stavu přístupů/test dostupnosti/platnosti přihlašovacích údajů
funkce testování že zbývá víc než 0 přístupů - ověření aktuálního stavu přístupů

přihlašovací údaje
jméno
heslo skrýt hvězdičkou - wiget password
aktuální počet přístupů



view
res.partner
přidat nové sloupce monitoring a microreport na form res.partner sekci monitoring zobrazovat když je bool true, sekci microreport zobrazovat když je
přidání ikon
úprava css
úprava kanban + ikony, hvězdičky


cribis_monitoring

cribis_microreport


přidání funkce stažení monitoringu do odoo cronu
přidání funkce stažení microreportu pro všechny změny group společnosti


