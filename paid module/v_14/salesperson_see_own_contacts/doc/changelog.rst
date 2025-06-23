.. _changelog:

Changelog
=========
`Version 0.2 (Wed Jan 29 14:53:22 2020)`
----------------------------------------
- [IMP] For users who have HR module installed, this version resolves the issue where admin cannot see any contact including the users`.
  NB: If you are upgrading from 12.0.1.0 to 12.0.0.2 you may have to UPGRADE the Odoo `base` module if you encounter a `missing record` error
- [IMP] New `User group` added to have a standalone group for `See Own Contacts`.
- [IMP] Salesperson who belong to 'own contacts' group shall see contacts of fellow workmates (internal users) by default in order to be able to collaborate easily.

`Version 0.1`
----------------------------------------
- [IMP] `domain force` improved to include followers of the commercial partner of the user.
