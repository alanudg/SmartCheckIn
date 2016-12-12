(function() {
    var AdminForm = function() {
        // Field converters
        var fieldConverters = [];

        /**
         * Process Leaflet (map) widget
         */
        function processLeafletWidget($el, name) {
            // if (!window.MAPBOX_MAP_ID) {
            //   console.error("You must set MAPBOX_MAP_ID in your Flask settings to use the map widget");
            //   return false;
            // }

            var geometryType = $el.data("geometry-type")
            if (geometryType) {
                geometryType = geometryType.toUpperCase();
            } else {
                geometryType = "GEOMETRY";
            }
            var multiple = geometryType.lastIndexOf("MULTI", geometryType) === 0;
            var editable = !$el.is(":disabled");

            var $map = $("<div>").width($el.data("width")).height($el.data("height"));
            $el.after($map).hide();

            var center = null;
            if ($el.data("lat") && $el.data("lng")) {
                center = L.latLng($el.data("lat"), $el.data("lng"));
            }

            var maxBounds = null;
            if ($el.data("max-bounds-sw-lat") && $el.data("max-bounds-sw-lng") &&
                $el.data("max-bounds-ne-lat") && $el.data("max-bounds-ne-lng")) {
                maxBounds = L.latLngBounds(
                    L.latLng($el.data("max-bounds-sw-lat"), $el.data("max-bounds-sw-lng")),
                    L.latLng($el.data("max-bounds-ne-lat"), $el.data("max-bounds-ne-lng"))
                )
            }

            var editableLayers;
            if ($el.val()) {
                editableLayers = new L.geoJson(JSON.parse($el.val()));
                center = center || editableLayers.getBounds().getCenter();
            } else {
                editableLayers = new L.geoJson();
            }

            var mapOptions = {
                center: center,
                zoom: ($el.data("zoom") && $el.data("zoom") < 18) ? $el.data("zoom") : 18,
                minZoom: $el.data("min-zoom"),
                maxZoom: $el.data("max-zoom"),
                maxBounds: maxBounds
            }
            if (!editable) {
                mapOptions.dragging = false;
                mapOptions.touchzoom = false;
                mapOptions.scrollWheelZoom = false;
                mapOptions.doubleClickZoom = false;
                mapOptions.boxZoom = false;
                mapOptions.tap = false;
                mapOptions.keyboard = false;
                mapOptions.zoomControl = false;
            }

            // only show attributions if the map is big enough
            // (otherwise, it gets in the way)
            if ($map.width() * $map.height() < 10000) {
                mapOptions.attributionControl = false;
            }

            var map = L.map($map.get(0), mapOptions)
            map.addLayer(editableLayers);
            if (center) {
                // if we have more than one coordenadas, make the map show everything
                var bounds = editableLayers.getBounds()
                if (!bounds.getNorthEast().equals(bounds.getSouthWest())) {
                    map.fitBounds(bounds, {maxZoom : 18});
                }
            } else {
                // look up user's location by IP address
                $.getJSON("//ip-api.com/json/?callback=?", function(data) {
                    map.setView([data["lat"], data["lon"]], 12);
                }).fail(function() {
                    map.setView([0, 0], 1)
                });
            }

            // set up tiles
            var mapboxVersion = window.MAPBOX_ACCESS_TOKEN ? 4 : 3;
            L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; <a href="http://openstreetmap.org/copyright">OpenStreetMap</a> contributors',
                maxZoom: 18
            }).addTo(map);


            // everything below here is to set up editing, so if we're not editable,
            // we can just return early.
            if (!editable) {
                return true;
            }

            // set up Leaflet.draw editor
            var drawOptions = {
                draw: {
                    // circles are not geometries in geojson
                    circle: false
                },
                edit: {
                    featureGroup: editableLayers
                }
            }

            var drawControl = new L.Control.Draw({
                edit: false,
                draw: {
                    polygon: {
                        allowIntersection: false,
                        showArea: false
                    },
                    polyline: false,
                    rectangle: false,
                    circle: false,
                    marker: false,
                }
            });
            var editControl = new L.Control.Draw({
                edit: {
                    featureGroup: editableLayers,
                },
                draw: false,
            });

            if ($.inArray(geometryType, ["POINT", "MULTIPOINT"]) > -1) {
                drawOptions.draw.polyline = false;
                drawOptions.draw.polygon = false;
                drawOptions.draw.rectangle = false;
            } else if ($.inArray(geometryType, ["LINESTRING", "MULTILINESTRING"]) > -1) {
                drawOptions.draw.marker = false;
                drawOptions.draw.polygon = false;
                drawOptions.draw.rectangle = false;
            } else if ($.inArray(geometryType, ["POLYGON", "MULTIPOLYGON"]) > -1) {
                drawOptions.draw.marker = false;
                drawOptions.draw.polyline = false;
            }
            // var drawControl = new L.Control.Draw(drawOptions);
            if ($el.val()) {
              map.addControl(editControl);
            }else{
              map.addControl(drawControl);
            }

            if (window.google) {
                var geocoder = new google.maps.Geocoder();

                function googleGeocoding(text, callResponse) {
                    geocoder.geocode({
                        address: text
                    }, callResponse);
                }

                function filterJSONCall(rawjson) {
                    var json = {},
                        key, loc, disp = [];
                    for (var i in rawjson) {
                        key = rawjson[i].formatted_address;
                        loc = L.latLng(rawjson[i].geometry.location.lat(),
                            rawjson[i].geometry.location.lng());
                        json[key] = loc;
                    }
                    return json;
                }

                map.addControl(new L.Control.Search({
                    callData: googleGeocoding,
                    filterJSON: filterJSONCall,
                    markerLocation: true,
                    autoType: false,
                    autoCollapse: true,
                    minLength: 2,
                    zoom: 10
                }));
            }


            // save when the editableLayers are edited
            var saveToTextArea = function() {
                var geo = editableLayers.toGeoJSON();
                if (geo.features.length === 0) {
                    $el.val("");
                    return true
                }
                if (multiple) {
                    var coords = $.map(geo.features, function(feature) {
                        return [feature.geometry.coordinates];
                    })
                    geo = {
                        "type": geometryType,
                        "coordinates": coords
                    }
                } else {
                    geo = geo.features[0].geometry;
                }
                $el.val(JSON.stringify(geo));
            }

            // handle creation
            map.on('draw:created', function(e) {

                map.removeControl(drawControl);
                map.addControl(editControl);

                if (!multiple) {
                    editableLayers.clearLayers();
                }
                editableLayers.addLayer(e.layer);
                saveToTextArea();
            })
            map.on('draw:edited', function() {
                map.removeControl(editControl);
                map.addControl(drawControl);
                saveToTextArea();
            });
            map.on('draw:deleted', saveToTextArea);
        }

        /**
         * Process data-role attribute for the given input element. Feel free to override
         *
         * @param {Selector} $el jQuery selector
         * @param {String} name data-role value
         */
        this.applyStyle = function($el, name) {
            // Process converters first
            for (var conv in fieldConverters) {
                var fieldConv = fieldConverters[conv];

                if (fieldConv($el, name))
                    return true;
            }

            // make x-editable's POST compatible with WTForms
            // for x-editable, x-editable-combodate, and x-editable-boolean cases
            var overrideXeditableParams = function(params) {
                var newParams = {};
                newParams['list_form_pk'] = params.pk;
                newParams[params.name] = params.value;
                if ($(this).data('csrf')) {
                    newParams['csrf_token'] = $(this).data('csrf');
                }
                return newParams;
            }

            switch (name) {
                case 'leaflet':
                    processLeafletWidget($el, name);
                    return true;
            }
        };

        /**
         * Add inline form field
         *
         * @method addInlineField
         * @param {Node} el Button DOM node
         * @param {String} elID Form ID
         */
        this.addInlineField = function(el, elID) {
            // Get current inline field
            var $el = $(el).closest('.inline-field');
            // Figure out new field ID
            var id = elID;

            var $parentForm = $el.parent().closest('.inline-field');

            if ($parentForm.hasClass('fresh')) {
                id = $parentForm.attr('id');
                if (elID) {
                    id += '-' + elID;
                }
            }

            var $fieldList = $el.find('> .inline-field-list');
            var maxId = 0;

            $fieldList.children('.inline-field').each(function(idx, field) {
                var $field = $(field);

                var parts = $field.attr('id').split('-');
                idx = parseInt(parts[parts.length - 1], 10) + 1;

                if (idx > maxId) {
                    maxId = idx;
                }
            });

            var prefix = id + '-' + maxId;

            // Get template
            var $template = $($el.find('> .inline-field-template').text());

            // Set form ID
            $template.attr('id', prefix);

            // Mark form that we just created
            $template.addClass('fresh');

            // Fix form IDs
            $('[name]', $template).each(function(e) {
                var me = $(this);

                var id = me.attr('id');
                var name = me.attr('name');

                id = prefix + (id !== '' ? '-' + id : '');
                name = prefix + (name !== '' ? '-' + name : '');

                me.attr('id', id);
                me.attr('name', name);
            });

            $template.appendTo($fieldList);

            // Select first field
            $('input:first', $template).focus();

            // Apply styles
            this.applyGlobalStyles($template);
        };

        /**
         * Apply global input styles.
         *
         * @method applyGlobalStyles
         * @param {Selector} jQuery element
         */
        this.applyGlobalStyles = function(parent) {
            var self = this;

            $(':input[data-role], a[data-role]', parent).each(function() {
                var $el = $(this);
                self.applyStyle($el, $el.attr('data-role'));
            });
        };

        /**
         * Add a field converter for customizing styles
         *
         * @method addFieldConverter
         * @param {converter} function($el, name)
         */
        this.addFieldConverter = function(converter) {
            fieldConverters.push(converter);
        };
    };

    // Add on event handler
    $('body').on('click', '.inline-remove-field', function(e) {
        e.preventDefault();

        var form = $(this).closest('.inline-field');
        form.remove();
    });

    // Expose faForm globally
    var faForm2 = window.faForm2 = new AdminForm();

})();

function debounce(func, wait, immediate) {
    var timeout;
    return function() {
        var context = this,
            args = arguments;
        var later = function() {
            timeout = null;
            if (!immediate) func.apply(context, args);
        };
        var callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(context, args);
    };
};
var aplicarOSM = debounce(function() {
    var aplicado = false;
    // TODO
    // Arreglar el zoom en el listado de mapas
    if ($("#coordenadas").parent().find("div").length) {
        $("[data-geometry-type='Polygon'], #coordenadas").each(function(k, v) {
            var $el = $(v);
            $el.val($el.val().replace(/(\\\"{1})/g, '\"').replace(/\"\{/g, '{').replace(/\}\"/g, '}'));
        });
        $("#coordenadas").parent().find("div").remove();
        aplicado = true;
        faForm2.applyGlobalStyles();
    }else if($("[data-geometry-type='Polygon']").attr('disabled') == 'disabled'){
      if($("[data-geometry-type='Polygon']").parent().find("div").length){
        $("[data-geometry-type='Polygon']").parent().find("div").remove();
        aplicado = true;
        faForm2.applyGlobalStyles();
      }
    }
    if (!aplicado) {
        aplicarOSM();
    }
}, 100);
aplicarOSM();
