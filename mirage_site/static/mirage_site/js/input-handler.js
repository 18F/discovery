// https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Strict_mode
'use strict';

var InputHandler = {
    init: function() {
        this.populateDropDown();

        // event bindings
        $('#naics-code').change(this.sendCodeChange.bind(InputHandler));
        $('#setaside-filters').change(this.sendFilterChange);
        $('form#vehicle-select select').change(this.sendVehicleChange.bind(InputHandler));
        //should this be bound to the InputHandler? KBD
        $('#vendor_contract_history_title_container').on('click', 'div.contracts_button', this.sendContractsChange);
        $('#vendor_contract_history_title_container').on('keypress', 'div.contracts_button', this.sendContractsChange);
        $('#ch_table').on('click', 'th.sortable', this.sortContracts);
        $('#ch_table').on('keypress', 'th.sortable', this.sortContracts);


        Events.subscribe('loadedWithQS', this.updateFields.bind(InputHandler));
    },

    updateFields: function(obj) {
        var setasides, i, len;

        if (obj['naics-code'] !== null) {
            $('#naics-code').select2('val', obj['naics-code']);
            this.naicsCode = obj['naics-code'];
        }

        if (obj.setasides) {
            setasides = obj.setasides.split(',');
            len = setasides.length - 1;

            for (i = 0; i < len; i++) {
                $('input[value=' + setasides[i] + ']').attr('checked', 'checked');
            }
        }

        if(obj.vehicle){
            this.vehicle = obj['vehicle'];
            $('form#vehicle-select select').val(obj['vehicle']);
        }
    },

    sortContracts: function(e) {
        //if enter pressed or if click then sort
        if ((e.type == "keypress" && e.charCode == 13) || e.type == "click") {
            var $target = $(e.target);
            var data = {
                'naics': this.naicsCode,
                'listType': 'naics',
            }
            var class_map = {
                'h_date_signed': 'date',
                'h_agency': 'agency',
                'h_value': 'amount',
                'h_status': 'status',
            }

            var classes = $target.attr('class').split(' ');
            data['page'] = 1;
            data['sort'] = class_map[classes[0]];

            if ($target.hasClass('arrow-down')) {
                data['direction'] = 'asc'
                $target.removeClass('arrow-down').addClass('arrow-up').attr("title", "Sorted ascending");
            } else if ($target.hasClass('arrow-sortable')) {
                data['direction'] = 'desc'
                $target.removeClass('arrow-sortable').addClass('arrow-down').attr("title", "Sorted descending");
            } else {
                data['direction'] = 'desc'
                $target.removeClass('arrow-up').addClass('arrow-down').attr("title", "Sorted descending")
            }

            //reset other ths that are sortable
            $target.siblings('.sortable').removeClass('arrow-down').removeClass('arrow-up').addClass('arrow-sortable').attr("title", "Select to sort");

            //prevent button flipping by selecting proper listType
            var $button = $("#vendor_contract_history_title_container").find('.contracts_button_active');
            if ($button.text() == "All Contracts") { data['listType'] = 'all'; }
            else { data['listType'] = 'naics'; }

            Events.publish('contractsChanged', data);

        }
    },

    sendContractsChange: function(e) {
        if ((e.type == "keypress" && e.charCode == 13) || e.type == "click") {
            var listType = 'naics';
            if(e.target.textContent == "All Contracts" || e.target.innerText == "All Contracts"){
                this.naicsCode = 'all';
                listType = 'all';
            } else {
                this.naicsCode = $("#vendor_contract_history_title_container").find("div").first().text().replace("NAICS", '').trim();
            }

            //reset date header column classes
            var $date = $("div#ch_table th.h_date_signed");
            $date.removeClass('arrow-sortable').addClass('arrow-down').attr("title", "Sorted descending");
            $date.siblings('.sortable').removeClass('arrow-down').removeClass('arrow-up').addClass('arrow-sortable').attr("title", "Select to sort");

            Events.publish('contractsChanged', {'page': 1, 'naics': this.naicsCode, 'listType': listType});
            return false;
        }
    },

    sendVehicleChange: function(e) {
        this.vehicle = $('form#vehicle-select select').val(); //to get the default
        Events.publish('vehicleChanged', {'vehicle': this.vehicle, 'vehicleOnly': true});
    },

    sendCodeChange: function(e) {
        this.naicsCode = e.val;
        Events.publish('naicsChanged');
    },

    sendFilterChange: function(e) {
        Events.publish('filtersChanged');
    },

    getVehicle: function() {
        return this.vehicle;
    },

    getNAICSCode: function() {
        return this.naicsCode;
    },

    getSetasides: function() {
        /* returns array of setaside ids that are checked */
        var setasides = [];
        $("form#setaside-filters input:checked").each( function(index) {
            setasides.push($(this).val());
        });

        return setasides;
    },

    populateDropDown: function() {
        // can't seem to use cached jqobj, something goes wrong with select2
        this.populatePromise = RequestsManager.getAPIRequest(
            "/api/naics/",
            { format: "json" },
            function( data ) {
                $.each(data.results, function(key, result) {
                    $("#naics-code")
                         .append($("<option></option>")
                         .attr("value", result.short_code)
                         .text(result.short_code + " - " + result.description));
                });
                //load data if search criteria is defined in querystring
                if (URLManager.getParameterByName("naics-code") || URLManager.getParameterByName("setasides")) {
                    Events.publish('loadData');
                }
                $("#naics-code")
                    .select2({placeholder:'Select a NAICS code', width : '380px'})
                    .select2("val", URLManager.getParameterByName("naics-code"));
            }
        );
        $('#naics-code').select2({placeholder:'Select a NAICS code', width : '380px'});
    },

    /*
     * This function is asynchronous because getting the selected NAICS text
     * depends on having populated the dropdown via a JSON request. Usage:
     *
     * InputHandler.getSelectedNAICS(function(text) {
     *   // do something with text here
     * });
     */
    getSelectedNAICS: function(callback) {
        this.populatePromise.done(function() {
            var text = $("#naics-code option:selected").text();
            callback(text);
        });
    }
};
