borg-erp-6of3 OpenERP6.1
=========================

*server == https://code.launchpad.net/~ocb/ocb-server/6.1 
*web == https://code.launchpad.net/~ocb/ocb-web/6.1
*addons == https://code.launchpad.net/~ocb/ocb-addons/6.1 
  l10n_coa <= all l10n_* moved to l10n_coa as temporary solution
  addons_oe <= OpenERP internal modules moved to addons_oe
*l10n_coa - temp COAs place. Generaly people are not interested in COA changes in other continent
*l10n_eu - place for EU specific full modules, or common skeletons for localizations (intrastat_base for example)
*l10n_* - localizations per country with COAs

##base - addons/module_name_base
       - fixing wontfix, ovrerride methods, views, introduce new mixins ...
       - so the base can become all that was expected from core server,web and addons

##addons_oca 
       - account_oca: oca modules 
         if the functionality is needed in 50%+ of your implemetations and in next 20% you can live with it (groups=...or options) vote YES to reduce complexity
          
##addons_oca_extra
       - account_functionality:  not so commonly used.

Good place to check new ideas is Tryton 3.0.


