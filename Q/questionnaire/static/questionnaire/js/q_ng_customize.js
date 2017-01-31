/* q_ng_project.js */
/* ng app for dealing w/ QProjects */

(function() {
    var app = angular.module("q_customizer", ["q_base"]);

    /**********/
    /* CONFIG */
    /**********/

    app.config(['$httpProvider', '$provide', function($httpProvider, $provide) {

        /* TODO: MOVE THIS AJAX LOGIC INTO q_base */
        $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        $httpProvider.defaults.xsrfCookieName = 'csrftoken';
        $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';

        /* I have to admit to not fully understanding how this code works */
        /* but it allows uibAccordion to work w/ ui-sortable */
        /* (https://stackoverflow.com/questions/26520131/how-can-i-create-a-sortable-accordion-with-angularjs/27637542#27637542) */
        $provide.decorator('uibAccordionDirective', function($delegate) {
           var directive = $delegate[0];
            directive.replace = true;
            return $delegate;
        });

    }]);

    /*************/
    /* FACTORIES */
    /*************/

    /***************/
    /* CONTROLLERS */
    /***************/

    /************************/
    /* top level controller */
    /************************/

    app.controller("CustomizerController", [ "$http", "$global_services", "$scope", function($http, $global_services, $scope) {

        $scope.blocking = function() {
            return $global_services.getBlocking();
        };

        /* look here - I am passing "customizer_id" to this controller */
        /* it is used throughout the code, as a query parameter to the RESTful API */
        /* this is a global variable in the template (set via Django) */
        /* I don't think that this is the "AngularJS-Approved" way of doing things */
        /* see: http://stackoverflow.com/questions/14523679/can-you-pass-parameters-to-an-angularjs-controller-on-creation */

        var project_controller = this;

        project_controller.project = {};  // initial data
        project_controller.documents = []; // initial data
        project_controller.customizations = []; // initial data
        project_controller.ontologies = []; // initial data (includes proxies)

        project_controller.selected_document_ontology = {};
        project_controller.selected_document_proxy = {};
        project_controller.selected_customization_ontology = {};
        project_controller.selected_customization_proxy = {};

        project_controller.customization_sort_type = "name";
        project_controller.customization_sort_reverse = false;
        project_controller.document_sort_type = "label";
        project_controller.document_sort_reverse = false;

        project_controller.has_default_customization = false;
        project_controller.has_unsynchronized_customization = false;
        project_controller.has_unsynchronized_document = false;
        project_controller.has_incomplete_document = false;

        this.selected_document_ontology_changed = function() {
            project_controller.selected_document_proxy = {};
            $("#document_proxy").addClass("q-dirty");
            /* disable the link w/ extreme prejudice */
            $('#create_document').addClass('btn-disabled');
            $('#create_document').attr('disabled', 'disabled');
            $('#create_document').prop('disabled', true);
            $('#create_document').click(function(e) {
                e.preventDefault();
            });
        };

        this.selected_document_proxy_changed = function() {
            $("#document_proxy").removeClass("q-dirty");
            /* re-enable the link */
            $('#create_document').removeClass('btn-disabled');
            $('#create_document').removeAttr('disabled');
            $('#create_document').prop('disabled', false);
            $('#create_document').unbind('click').click();
        };

        this.selected_customization_ontology_changed = function() {
            project_controller.selected_customization_proxy = {};
            /* disable the link w/ extreme prejudice */
            $('#create_customization').addClass('btn-disabled');
            $('#create_customization').attr('disabled', 'disabled');
            $('#create_customization').prop('disabled', true);
            $('#create_customization').click(function(e) {
                e.preventDefault();
            });
        };

        this.selected_customization_proxy_changed = function() {
            /* re-enable the link */
            $('#create_customization').removeClass('btn-disabled');
            $('#create_customization').removeAttr('disabled');
            $('#create_customization').prop('disabled', false);
            $('#create_customization').unbind('click').click();
        };

        this.change_document_sort_type = function(sort_type) {
            project_controller.document_sort_type = sort_type;
            project_controller.document_sort_reverse = !(project_controller.document_sort_reverse);
        };

        this.change_customization_sort_type = function(sort_type) {
            project_controller.customization_sort_type = sort_type;
            project_controller.customization_sort_reverse = !(project_controller.customization_sort_reverse);
        };

        this.load = function() {
            $http.get("/api/projects/" + project_id, {format: "json"})
                .success(function (data) {
                    project_controller.project = data;
                })
                .error(function (data) {
                    console.log(data);
                });
/*
            $http.get("/api/customizations_lite/?ordering=name&project=" + project_id, {format: "json"})
                .success(function (data) {
                    project_controller.customizations = data.results;
                    $.each(project_controller.customizations, function(i, c) {
                        if (c.synchronization.length) {
                            project_controller.has_unsynchronized_customization = true;
                        }
                        if (c.is_default) {
                            project_controller.has_default_customization = true;
                        }
                        if (project_controller.has_unsynchronized_customization && project_controller.has_default_customization) {
                            return false;  // break out of the loop if we've already found matches
                        }
                    });
                })
                .error(function (data) {
                    console.log(data);
                });
*/
/*
            $http.get("/api/realizations_lite/?project=" + project_id, {format: "json"})
                .success(function (data) {
                    project_controller.documents = data.results;
                    $.each(project_controller.documents, function(i, d) {
                        if (d.synchronization.length) {
                            project_controller.has_unsynchronized_document = true;
                        }
                        if (!d.is_complete) {
                            project_controller.has_incomplete_document = true;
                        }
                        if (project_controller.has_unsynchronized_document && project_controller.has_incomplete_document) {
                            return false;  // break out of the loop if we've already found matches
                        }
                    });
                })
                .error(function (data) {
                    console.log(data);
                });
*/
            $http.get("/api/ontologies/?is_registered=true&project=" + project_id, {format: "json"})
                .success(function (data) {
                    var ontologies = data.results;
                    project_controller.ontologies = ontologies;
                    if (data.count) {
                        project_controller.selected_document_ontology = ontologies[0];
                        project_controller.selected_document_proxy = ontologies[0].document_types[0];
                        project_controller.selected_customization_ontology = ontologies[0];
                        project_controller.selected_customization_proxy = ontologies[0].document_types[0];
                    }

                })
                .error(function (data) {
                    console.log(data);
                });
        };

        project_controller.load();

        this.document_publish = function(document) {
            $global_services.setBlocking(true);
            var publish_document_request_url = "/services/realization_publish/";
            var publish_document_request_data = $.param({
                "document_id": document.id
            });

            $http({
                method: 'POST',
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                url: publish_document_request_url,
                data: publish_document_request_data
            }).success(function(data) {
                project_controller.load();
                check_msg();
            })
            .error(function(data) {
                console.log(data);
                check_msg();
            })
            .finally(function() {
                $global_services.setBlocking(false);
            });

        };

        this.project_join_request = function(user_id) {
            $global_services.setBlocking(true);
            var project_join_request_url =
                "/services/" + project_controller.project.name +
                "/project_join_request/";
            var project_join_request_data = $.param({
                user_id: user_id
            });

            $http({
                method: 'POST',
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                url: project_join_request_url,
                data: project_join_request_data
            }).success(function(data) {
                check_msg();
            })
            .error(function(data) {
                console.log(data);
                check_msg();
            })
            .finally(function() {
                $global_services.setBlocking(false);
            });

        };

        this.customization_delete = function(customization) {
            var msg = "This will permanently delete this customization.  Are you sure you wish to continue?"
            bootbox.confirm(msg, function(result) {
                if (! result) {
                    show_lil_msg("Good thinking.");
                }
                else {
                    $global_services.setBlocking(true);
                    var customization_delete_url = "/services/customization_delete/";
                    var customization_delete_data = $.param({
                        "customization_id": customization.id
                    });

                    $http({
                        method: 'POST',
                        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                        url: customization_delete_url,
                        data: customization_delete_data
                    }).success(function(data) {
                        project_controller.load();
                        check_msg();
                    })
                    .error(function(data) {
                        console.log(data);
                        check_msg();
                    })
                    .finally(function() {
                        $global_services.setBlocking(false);
                    });
                }
            });
        };

    }]);

    /***********/
    /* THE END */
    /***********/

})();