/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { debounce } from "@web/core/utils/timing";

publicWidget.registry.PortalPopover = publicWidget.Widget.extend({
    selector: "#wrapwrap",

    start() {
        this.$el.on('mouseenter', '.pop', debounce(this._onMouseEnter.bind(this), 100));
        this.$el.on('mouseleave', '.pop', this._onMouseLeave.bind(this));
        return this._super(...arguments);
    },

    _onMouseEnter(ev) {
        const $target = $(ev.currentTarget);
        const $popoverContent = $target.next('.popover-hidden-content');

        if (!$popoverContent.length) return;

        const htmlContent = $popoverContent.html() || '';

        if (!$target.data('bs.popover')) {
            $target.popover({
                trigger: 'manual',
                html: true,
                placement: 'auto',
                container: 'body',
                content: `<div class="popover-body">${htmlContent}</div>`,
            }).on('shown.bs.popover', () => {
                const popoverId = $target.attr('aria-describedby');
                const $popoverEl = $(`#${popoverId}`);

                if ($popoverEl.length) {
                    $popoverEl.on('mouseenter', () => {
                        clearTimeout($target.data('hide-timeout'));
                    });

                    $popoverEl.on('mouseleave', () => {
                        $target.popover('hide');
                    });
                }
            });
        }
        $target.popover('show');
    },

    _onMouseLeave(ev) {
        const $target = $(ev.currentTarget);
        const timeout = setTimeout(() => {
            $target.popover('hide');
        }, 200);
        $target.data('hide-timeout', timeout);
    },
});
