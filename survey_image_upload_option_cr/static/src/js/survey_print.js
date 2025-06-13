/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { rpc } from "@web/core/network/rpc";
import {
    parseDate,
    serializeDate,
    parseDateTime,
    serializeDateTime
} from "@web/core/l10n/dates";

const SurveyFormWidget = publicWidget.registry.SurveyFormWidget;

if (SurveyFormWidget) {
    SurveyFormWidget.include({

        start() {
            this._super(...arguments);
            console.log('---first-----------reload page')
            this._tryRestoreFormData();  // Attempt restore on start
            console.log('---second-----------reload page')
        },

        async _tryRestoreFormData() {
            const cached = localStorage.getItem("survey_form_backup");
            if (cached) {
                const cachedParams = JSON.parse(cached);

                console.log("🔄 Restoring survey data from localStorage...", cachedParams);

                // Optional: auto-submit after reload
                if (confirm("Restore previous form submission?")) {
                    await rpc(
                        `/survey/submit/${this.options.surveyToken}/${this.options.answerToken}`,
                        cachedParams
                    );
                    localStorage.removeItem("survey_form_backup");
                    location.reload();  // Or call `this._nextScreen()` if needed
                }
            }
        },

        _submitForm: async function (options) {
            var params = {};
            if (options.previousPageId) {
                params.previous_page_id = options.previousPageId;
            }
            if (options.nextSkipped) {
                params.next_skipped_page_or_question = true;
            }

            var route = "/survey/submit";

            if (this.options.isStartScreen) {
                route = "/survey/begin";
                if (this.options.questionsLayout === 'page_per_question') {
                    this.$('.o_survey_main_title').fadeOut(400);
                }
            } else {
                const $form = this.$('form');
                const formData = new FormData($form[0]);

                if (!options.skipValidation) {
                    if (!this._validateForm($form, formData)) {
                        return;
                    }
                }

                await this._prepareSubmitValues(formData, params);
            }

            this.preventEnterSubmit = true;

            if (this.options.sessionInProgress) {
                this.fadeInOutDelay = 400;
                this.readonly = true;
            }

            // Save to localStorage before RPC
            localStorage.setItem("survey_form_backup", JSON.stringify(params));

            const submitPromise = rpc(
                `${route}/${this.options.surveyToken}/${this.options.answerToken}`,
                params
            );

            if (!this.options.isStartScreen && this.options.scoringType === 'scoring_with_answers_after_page') {
                const [correctAnswers] = await submitPromise;
                if (Object.keys(correctAnswers).length && document.querySelector('.js_question-wrapper')) {
                    this._showCorrectAnswers(correctAnswers, submitPromise, options);
                    localStorage.removeItem("survey_form_backup");
                    return;
                }
            }

            localStorage.removeItem("survey_form_backup");
            this._nextScreen(submitPromise, options);
        },

        _prepareSubmitValues: async function (formData, params) {
            var self = this;

            // Copy CSRF and static values
            formData.forEach(function (value, key) {
                switch (key) {
                    case 'csrf_token':
                    case 'token':
                    case 'page_id':
                    case 'question_id':
                        params[key] = value;
                        break;
                }
            });

            const elements = Array.from(this.$('[data-question-type]'));

            for (const el of elements) {
                const $el = $(el);
                const questionType = $el.data('questionType');

                switch (questionType) {
                    case 'text_box':
                    case 'char_box':
                    case 'numerical_box':
                        params[el.name] = el.value;
                        break;

                    case 'date':
                    case 'datetime': {
                        const [parse, serialize] =
                            questionType === "date"
                                ? [parseDate, serializeDate]
                                : [parseDateTime, serializeDateTime];
                        const date = parse(el.value);
                        params[el.name] = date ? serialize(date) : "";
                        break;
                    }

                    case 'scale':
                    case 'simple_choice_radio':
                    case 'multiple_choice':
                        params = self._prepareSubmitChoices(params, $el, $el.data('name'));
                        break;

                    case 'matrix':
                        params = self._prepareSubmitAnswersMatrix(params, $el);
                        break;

                    case 'file': {
                        const fileInput = el;
                        const files = fileInput.files;
                        const inputName = fileInput.name;

                        if (!files || files.length === 0) break;

                        params[inputName] = [];
                        params[`filename`] = [];

                        for (const file of files) {
                            const base64String = await new Promise((resolve, reject) => {
                                const reader = new FileReader();
                                reader.onload = function (event) {
                                    resolve(event.target.result);
                                };
                                reader.onerror = function (error) {
                                    reject(error);
                                };
                                reader.readAsDataURL(file);
                            });
                            params[inputName].push(base64String);
                            params[`filename`].push(file.name);
                        }

                        break;
                    }
                }
            }

            console.log("✅ Form params prepared:", params);
        },

    });
} else {
    console.warn("⚠️ SurveyFormWidget not found.");
}
