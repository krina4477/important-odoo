/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.LoadMoreQuestions = publicWidget.Widget.extend({
    selector: '.qa-wrapper',

    events: {
        'click #loadMoreBtn': '_onLoadMoreClick',
        'click #loadMoreFAQsBtn': '_onLoadMoreFAQsClick',
        'click #searchInQA': '_onSearchQA',
        
    },

    start() {
        this.qaLimit = 2;
        this.step = 2;
        this.qaItems = $('.qa-item');
        this.faItems = $('.faq-item');
        this.filteredQAItems = this.qaItems;
        return this._super(...arguments);
    },

    _onLoadMoreClick() {
        const hiddenItems = this.filteredQAItems.filter('.d-none');
        if (hiddenItems.length === 0) {
            this.filteredQAItems.addClass('d-none');
            this.filteredQAItems.slice(0, this.qaLimit).removeClass('d-none');
            $('#loadMoreBtn').text('Load More');
        } else {
            hiddenItems.slice(0, this.step).removeClass('d-none');
            if (this.filteredQAItems.filter('.d-none').length === 0) {
                $('#loadMoreBtn').text('Show Less');
            }
        }
    },

    _onLoadMoreFAQsClick() {
        const btn = document.getElementById('loadMoreFAQsBtn');
        const hiddenItem = document.querySelectorAll('.faq-item.d-none');
        if (!btn) return;
        hiddenItem.forEach(item => item.classList.remove('d-none'));
        btn.style.display = 'none';
    },

    _onSearchQA(ev) {
        const query = $('#qaSearch').val().toLowerCase();
        if (!query.trim()) {
            this.qaItems.addClass('d-none');
            this.qaItems.slice(0, this.qaLimit).removeClass('d-none');
            this.filteredQAItems = this.qaItems;
        }
        this.qaItems.addClass('d-none');
        this.filteredQAItems = this.qaItems.filter(function () {
            const question = $(this).find('.qa-question').text().toLowerCase();
            const answer = $(this).find('.qa-body').text().toLowerCase();
            return question.includes(query) || answer.includes(query);
        });
        this.filteredQAItems.slice(0, this.qaLimit).removeClass('d-none');
        this._checkbtnLoadMore();
    },    

    _checkbtnLoadMore() {
        const btn = document.getElementById('loadMoreBtn');
        if (!btn) return;
        const hiddenCount = this.filteredQAItems.filter('.d-none').length;
        if (hiddenCount === 0 || this.filteredQAItems.length <= this.qaLimit) {
            btn.hidden = true;
        } else {
            btn.hidden = false;
        }
    },
});
