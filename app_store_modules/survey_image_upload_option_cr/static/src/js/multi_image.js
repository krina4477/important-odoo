/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.OnlineSyncPortal = publicWidget.Widget.extend({
    selector: '.o_survey_form',

    events: {
        'change #image_upload_option': 'onClickUploadInput',
    },

    start: function () {
        console.log("📦 OnlineSyncPortal widget registered");
        this.uploadedFiles = [];
        return this._super(...arguments);
    },

    onClickUploadInput: function (e) {
        console.log('--onClickUploadInput triggered--');

        const $fileInput = this.$("#image_upload_option");
        const $previewList = this.$("#file-preview-list");
        const $limit = this.$("#upload-limit");

        if (!$fileInput.length || !$previewList.length) {
            console.warn("⚠️ Required elements not found");
            return;
        }

        this.fileInput = $fileInput[0];
        this.previewList = $previewList[0];
        this.limitMB = parseFloat($limit.data("limit-mb") || 0);
        this.limitBytes = this.limitMB * 1024 * 1024;

        this.handleFileChange();  // 🔁 Directly handle file change here
    },

    handleFileChange: function () {
        const selectedFiles = Array.from(this.fileInput.files);

        if (!this.fileInput.hasAttribute("multiple")) {
            this.uploadedFiles = [];
        }

        for (const file of selectedFiles) {
            const isDuplicate = this.uploadedFiles.some(f =>
                f.name === file.name &&
                f.size === file.size &&
                f.lastModified === file.lastModified
            );
            if (isDuplicate) {
                alert(`File "${file.name}" already added.`);
                continue;
            }

            if (this.limitMB > 0 && file.size > this.limitBytes) {
                alert(`File "${file.name}" exceeds ${this.limitMB} MB limit.`);
            } else {
                this.uploadedFiles.push(file);
            }
        }

        this.updateInputFiles();
        this.renderPreview();
    },

    updateInputFiles: function () {
        const dataTransfer = new DataTransfer();
        this.uploadedFiles.forEach(file => dataTransfer.items.add(file));
        this.fileInput.files = dataTransfer.files;
    },

    renderPreview: function () {
        this.previewList.innerHTML = "";
        const self = this;

        this.uploadedFiles.forEach((file, index) => {
            if (!file.type.startsWith("image/")) return;

            const card = document.createElement("div");
            card.className = "p-2 border rounded shadow-sm bg-light me-2 mb-2";
            card.style = "width: 160px; text-align: center;";

            const img = document.createElement("img");
            img.style = "max-width: 100%; max-height: 100px; object-fit: contain;";
            img.alt = file.name;

            const reader = new FileReader();
            reader.onload = (e) => {
                img.src = e.target.result;

                const downloadBtn = document.createElement("a");
                downloadBtn.href = e.target.result;
                downloadBtn.download = file.name;
                downloadBtn.className = "btn btn-sm btn-outline-primary w-100 mt-1";
                downloadBtn.innerText = "Download";

                card.appendChild(downloadBtn);
            };
            reader.readAsDataURL(file);

            const info = document.createElement("div");
            info.style = "font-size: 12px; margin-top: 5px;";
            info.textContent = `${file.name} (${(file.size / 1024).toFixed(1)} KB)`;

            const deleteBtn = document.createElement("button");
            deleteBtn.className = "btn btn-sm btn-outline-danger w-100 mt-1";
            deleteBtn.innerText = "Delete";
            deleteBtn.onclick = () => {
                self.uploadedFiles.splice(index, 1);
                self.updateInputFiles();
                self.renderPreview();
            };

            card.appendChild(img);
            card.appendChild(info);
            card.appendChild(deleteBtn);
            this.previewList.appendChild(card);
        });
    },
});
