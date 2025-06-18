//  Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
//  See LICENSE file for full copyright and licensing details.

(function () {
    "use strict";
    /*global document, window, console */
    function duplifer(element, options) {
        // Extend the default settings with user options
        var settings = Object.assign({
            colorGenerator: function (index) {
                // Predefined set of colors
                var r = (Math.round(Math.random() * 127) + 127).toString(16);
				var g = (Math.round(Math.random() * 127) + 127).toString(16);
				var b = (Math.round(Math.random() * 127) + 127).toString(16);
				return '#' + r + g + b;
            },
            highlightClass: "duplifer-highlightdups"
        }, options);

        // Get the data count from the element
        var dataCount = element.getAttribute('data-dcount');

        for (var i = 1; i <= dataCount; i++) {
            // Find index of the cell in the table header whose class matches the highlightClass + i
            var cellIndex = Array.from(element.querySelectorAll("thead tr th")).findIndex(th => th.classList.contains(settings.highlightClass + i));

            // Select all td elements that are in the same column as the matched th
            var rowTds = element.querySelectorAll(`tr td:nth-child(${cellIndex + 1})`);

            // Create an array of the values in each td
            var rowValues = Array.from(rowTds).map(td => td.innerHTML);

            // Find values that appear more than once (duplicates)
            var duplicates = rowValues.filter((value, index) => {
                return rowValues.lastIndexOf(value) === index && rowValues.indexOf(value) !== index;
            });

            // Assign the same color for the same value and store colors
            var colorMap = {};
            var colorIndex = 0;

            // Highlight the duplicates
            duplicates.forEach((duplicate) => {
                if (!colorMap[duplicate]) {
                    colorMap[duplicate] = settings.colorGenerator(colorIndex);
                    colorIndex++;
                }
                Array.from(rowTds).filter(td => {
                    // Skip empty fields
                    if (td.querySelector('div.o_field_empty')) {
                        return false;
                    }
                    return td.innerHTML === duplicate;
                }).forEach(td => {
                    td.style.backgroundColor = colorMap[duplicate];
                    td.classList.add('duplifer-highlighted');
                });
            });
        }
    }

    // Export the function to be used globally
    window.duplifer = duplifer;
})();
