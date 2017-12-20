// https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Strict_mode
'use strict';

var RequestsManager = {
    init: function() {
        Events.subscribe('naicsChanged', this.load.bind(RequestsManager));
        Events.subscribe('vehicleChanged', this.load.bind(RequestsManager));
        Events.subscribe('filtersChanged', this.load.bind(RequestsManager));
        Events.subscribe('loadedWithQS', this.load.bind(RequestsManager));
    },


    getAPIRequest: function(url, params, callback) {
        url = (APIHOST == 'None' ? '' : APIHOST) + url;
        params['api_key'] = APIKEY;
        return $.ajax({
              url: url,
              dataType: 'json',
              data: params
            })
            .done(callback)
            .fail(function(req, status, error) {
              if (!window.console) return;
              console.log('failed to load: ', url);
              console.log(error);
            });
    },

    buildRequestQuery: function() {
        var setasides = InputHandler.getSetasides();
        var naicsCode = InputHandler.getNAICSCode() || URLManager.getParameterByName('naics-code');
        var vehicle = InputHandler.getVehicle();
        var queryData = {};
        var pool = this.getPool();

        if (typeof naicsCode !== 'undefined') {
            queryData['naics'] = naicsCode;
        }

        if (setasides.length > 0) {
            queryData["setasides"] = setasides.join();
        }
        if (pool !== null) {
            queryData['pool'] = pool[0];
            queryData['vehicle'] = pool[1]
        }
        if (vehicle !== null) {
            queryData['vehicle'] = vehicle;
        }
        return queryData;
    },

    getPool: function() {
        var poolInfo = URLManager.getPoolInfo();

        if (poolInfo !== null){
            if (poolInfo['vehicle'] == 'oasissb'){
                return [poolInfo['pool_number'] + '_' + 'SB', poolInfo['vehicle']];
            }
            else {
                return [poolInfo['pool_number'], poolInfo['vehicle']];
            }
        }
        else {
            return null
        }
    }

};
