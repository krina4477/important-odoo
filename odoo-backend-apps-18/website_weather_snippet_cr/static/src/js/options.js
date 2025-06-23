/** @odoo-module **/

import "@web_editor/js/editor/snippets.options";

function __weatherwidget_init(a) {
    var a = a,
        i = [];
    if (0 !== a.length) {
        for (var t = function(t) {
                var e = a[t],
                    o = {};
                o.id = "weatherwidget-io-" + t, o.href = e.href, o.label_1 = e.getAttribute("data-label_1"), o.label_2 = e.getAttribute("data-label_2"), o.font = e.getAttribute("data-font"), o.icons = e.getAttribute("data-icons"), o.mode = e.getAttribute("data-mode"), o.days = e.getAttribute("data-days"), o.theme = e.getAttribute("data-theme"), o.basecolor = e.getAttribute("data-basecolor"), o.accent = e.getAttribute("data-accent"), o.textcolor = e.getAttribute("data-textcolor"), o.textAccent = e.getAttribute("data-textAccent"), o.highcolor = e.getAttribute("data-highcolor"), o.lowcolor = e.getAttribute("data-lowcolor"), o.suncolor = e.getAttribute("data-suncolor"), o.mooncolor = e.getAttribute("data-mooncolor"), o.cloudcolor = e.getAttribute("data-cloudcolor"), o.cloudfill = e.getAttribute("data-cloudfill"), o.raincolor = e.getAttribute("data-raincolor"), o.snowcolor = e.getAttribute("data-snowcolor"), o.windcolor = e.getAttribute("data-windcolor"), o.fogcolor = e.getAttribute("data-fogcolor"), o.thundercolor = e.getAttribute("data-thundercolor"), o.hailcolor = e.getAttribute("data-hailcolor"), o.dayscolor = e.getAttribute("data-dayscolor"), o.tempcolor = e.getAttribute("data-tempcolor"), o.desccolor = e.getAttribute("data-desccolor"), o.label1color = e.getAttribute("data-label1color"), o.label2color = e.getAttribute("data-label2color"), o.shadow = e.getAttribute("data-shadow"), o.scale = e.getAttribute("data-scale"), (r = document.getElementById(o.id)) && e.removeChild(r), i[o.id] = document.createElement("iframe"), i[o.id].setAttribute("id", o.id), i[o.id].setAttribute("class", "weatherwidget-io-frame"), i[o.id].setAttribute("title", "Weather Widget"), i[o.id].setAttribute("scrolling", "no"), i[o.id].setAttribute("frameBorder", "0"), i[o.id].setAttribute("width", "100%"), i[o.id].setAttribute("src", "https://weatherwidget.io/w/"), i[o.id].style.display = "block", i[o.id].style.position = "absolute", i[o.id].style.top = "0", i[o.id].onload = function() {
                    i[o.id].contentWindow.postMessage(o, "https://weatherwidget.io")
                }, e.style.display = "block", e.style.position = "relative", e.style.height = "150px", e.style.padding = "0", e.style.overflow = "hidden", e.style.textAlign = "left", e.style.textIndent = "-299rem", e.appendChild(i[o.id])
            }, e = 0, o = Math.min(a.length, 10); e < o; e++) {
            var r;
            t(e)
        }
        window.addEventListener("message", function(t) {
            "https://weatherwidget.io" === t.origin && i[t.data.wwId] && i[t.data.wwId].parentNode && (i[t.data.wwId].style.height = t.data.wwHeight + "px", i[t.data.wwId].parentNode.style.height = t.data.wwHeight + "px")
        })
    }
}

import { renderToElement } from "@web/core/utils/render";
import options from "@web_editor/js/editor/snippets.options";

options.registry.s_weather_snippet = options.Class.extend({
    updateUIVisibility: async function () {
        await this._super(...arguments);
        this.updateScript();
    },

    selectDataAttribute: function (previewMode, widgetValue, params) {
        this._super.apply(this, arguments);
        if (params.attributeName === 'listId' && previewMode === false) {
            this.$target.attr('data-list-id', widgetValue);
            var nbColumns = 'https://forecast7.com/en/'+ params.selectWidAttribute +'/'+ params.selectWnameAttribute + '/';
            this.$target.find('.a_weather_snippet').attr('href', nbColumns);
            this.$target.find('.a_weather_snippet').attr('data-label_1', params.selectNameAttribute)
        }
    },
    font: function (previewMode, widgetValue, params) {
        const nbColumns = widgetValue || 'Arial';
        this.$target.find('.a_weather_snippet').attr('data-font', nbColumns);
    },
    icons: function (previewMode, widgetValue, params) {
        const nbColumns = widgetValue || 'Iconvault';
        this.$target.find('.a_weather_snippet').attr('data-icons', nbColumns);
    },
    mode: function (previewMode, widgetValue, params) {
        const nbColumns = widgetValue || 'Both';
        this.$target.find('.a_weather_snippet').attr('data-mode', nbColumns);
    },
    days: function (previewMode, widgetValue, params) {
        const nbColumns = widgetValue || '7';
        this.$target.find('.a_weather_snippet').attr('data-days', nbColumns);
    },
    theme: function (previewMode, widgetValue, params) {
        const nbColumns = widgetValue || 'original';
        this.$target.find('.a_weather_snippet').attr('data-theme', nbColumns);
    },

    _getLabel: function () {
        return this.$target.find('.a_weather_snippet').attr('data-label_1') || 'NEW YORK';
    },
    _getselectDataAttributeId: function () {
        return this.$target.attr('data-list-id') || 0;
    },
    _getselectDataAttribute: function () {
        return this.$target.find('.a_weather_snippet').attr('href') || 'https://forecast7.com/en/40d71n74d01/new-york/';
    },
    _getFont: function () {
        return this.$target.find('.a_weather_snippet').attr('data-font') || 'Arial';
    },
    _getIcons: function () {
        return this.$target.find('.a_weather_snippet').attr('data-icons') || 'Iconvault';
    },
    _getMode: function () {
        return this.$target.find('.a_weather_snippet').attr('data-mode') || 'Both';
    },
    _getDays: function () {
        return this.$target.find('.a_weather_snippet').attr('data-days') || '7';
    },
    _getTheme: function () {
        return this.$target.find('.a_weather_snippet').attr('data-theme') || 'original';
    },

    _computeWidgetState: function (methodName, params) {
        switch (methodName) {
            case 'font': {
                return `${this._getFont()}`;
            }
            case 'selectDataAttribute': {
                return `${this._getselectDataAttributeId()}`;
            }
            case 'icons': {
                return `${this._getIcons()}`;
            }
            case 'mode': {
                return `${this._getMode()}`;
            }
            case 'days': {
                return `${this._getDays()}`;
            }
            case 'theme': {
                return `${this._getTheme()}`;
            }
        }
        return this._super(...arguments);
    },

    async _renderCustomXML(uiFragment) {
        this.cityLists = await this._rpc({
            model: 'weather.city',
            method: 'search_read',
            fields: ['id', 'name', 'weather_name','weather_id'],
            domain: [['weather_name', '!=', false], ['weather_id', '!=', false]],
        });
        if (this.cityLists.length) {
            const selectEl = uiFragment.querySelector('we-select[data-attribute-name="listId"]');
            for (const mailingList of this.cityLists) {
                const button = document.createElement('we-button');
                button.dataset.selectDataAttribute = mailingList.id;
                button.dataset.selectNameAttribute = mailingList.name;
                button.dataset.selectWidAttribute = mailingList.weather_id;
                button.dataset.selectWnameAttribute = mailingList.weather_name;
                button.textContent = mailingList.name;
                selectEl.appendChild(button);
            }
        }
    },
});

options.registry.countdown = options.Class.extend({
    events: Object.assign({}, options.Class.prototype.events || {}, {
        'click .toggle-edit-message': '_onToggleEndMessageClick',
    }),

    /**
     * Remove any preview classes, if present.
     *
     * @override
     */
    cleanForSave: async function () {
        this.$target.find('.s_countdown_canvas_wrapper').removeClass("s_countdown_none");
        this.$target.find('.s_countdown_end_message').removeClass("s_countdown_enable_preview");
    },

    /**
     * Changes the countdown action at zero.
     *
     * @see this.selectClass for parameters
     */
    endAction: function (previewMode, widgetValue, params) {
        this.$target[0].dataset.endAction = widgetValue;
        if (widgetValue === 'message' || widgetValue === 'message_no_countdown') {
            if (!this.$target.find('.s_countdown_end_message').length) {
                const message = this.endMessage || renderToElement('website.s_countdown.end_message');
                this.$target.append(message);
            }
            this.$target.toggleClass('hide-countdown', widgetValue === 'message_no_countdown');
        } else {
            const $message = this.$target.find('.s_countdown_end_message').detach();
            if (this.showEndMessage) {
                this._onToggleEndMessageClick();
            }
            if ($message.length) {
                this.endMessage = $message[0].outerHTML;
            }
        }
    },
    /**
    * Changes the countdown style.
    *
    * @see this.selectClass for parameters
    */
    layout: function (previewMode, widgetValue, params) {
        switch (widgetValue) {
            case 'circle':
                this.$target[0].dataset.progressBarStyle = 'disappear';
                this.$target[0].dataset.progressBarWeight = 'thin';
                this.$target[0].dataset.layoutBackground = 'none';
                break;
            case 'boxes':
                this.$target[0].dataset.progressBarStyle = 'none';
                this.$target[0].dataset.layoutBackground = 'plain';
                break;
            case 'clean':
                this.$target[0].dataset.progressBarStyle = 'none';
                this.$target[0].dataset.layoutBackground = 'none';
                break;
            case 'text':
                this.$target[0].dataset.progressBarStyle = 'none';
                this.$target[0].dataset.layoutBackground = 'none';
                break;
        }
        this.$target[0].dataset.layout = widgetValue;
    },

    /**
     * @override
     */
    updateUIVisibility: async function () {
        await this._super(...arguments);
        const dataset = this.$target[0].dataset;

        // End Action UI
        this.$el.find('.toggle-edit-message')
            .toggleClass('d-none', dataset.endAction === 'nothing' || dataset.endAction === 'redirect');

        // End Message UI
        this.updateUIEndMessage();
    },
    /**
     * @see this.updateUI
     */
    updateUIEndMessage: function () {
        this.$target.find('.s_countdown_canvas_wrapper')
            .toggleClass("s_countdown_none", this.showEndMessage === true && this.$target.hasClass("hide-countdown"));
        this.$target.find('.s_countdown_end_message')
            .toggleClass("s_countdown_enable_preview", this.showEndMessage === true);
    },

    /**
     * @override
     */
    _computeWidgetState: function (methodName, params) {
        switch (methodName) {
            case 'endAction':
            case 'layout':
                return this.$target[0].dataset[methodName];

            case 'selectDataAttribute': {
                if (params.colorNames) {
                    params.attributeDefaultValue = 'rgba(0, 0, 0, 255)';
                }
                break;
            }
        }
        return this._super(...arguments);
    },

    /**
     * @private
     */
    _onToggleEndMessageClick: function () {
        this.showEndMessage = !this.showEndMessage;
        this.$el.find(".toggle-edit-message")
            .toggleClass('text-primary', this.showEndMessage);
        this.updateUIEndMessage();
        this.trigger_up('cover_update');
    },
});
