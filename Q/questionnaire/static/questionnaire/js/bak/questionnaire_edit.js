/* functions specific to the editor & viewer */

var PREVIOUSLY_SELECTED_TAB = 0;

$.ui.dynatree.nodedatadefaults["icon"] = false; // Turn off icons by default


function panes(element) {
    // hide panes by default
    // only show them as the corresponding tree node is selected
    $(element).hide();
}


function autocompletes(element) {
    /* an autocomplete field stores the options as an attribute */
    /* parse those options and pass them to JQuery */
    var suggestions = $(element).attr("suggestions").split("|");
    $(element).autocomplete({
        source : suggestions
    });
    /* then add a visual indication that the field supports autocompletion */
    /* I use a standard JQuery icon, but move it down and left so that it resides w/in the field */
    $(element).after(
        "<span class='ui-icon ui-icon-carat-1-s' style='display: inline-block; margin-left: -16px; margin-bottom: -8px;' title='this field supports autocompletion'></span>"
    );
}


function references(element) {
    var options = $(element).find("option");
    $(options).each(function () {

        $(this).click(function () {
            var option = this;
            var input = $("<input type='text' class='reference_option_input'/>");
            $(input).val($(option).text());

            $(input).blur(function () {
                var input_value = $(this).val();
                $(option).val(input_value);
                $(option).text(input_value);  /* this implicitly removes the input element */
                $(option).show().focus();
            });

            $(option).text("");  /* this is how I hide the option (I can't actually use .hide() b/c the input is a child element and would be hidden too) */
            $(option).append(input);
            $(input).show().focus().select();
        });
    });
}


function dynamic_accordion_buttons(element) {

    if ( $(element).hasClass("add")) {
        $(element).button({
            icons: { primary : "ui-icon-circle-plus" },
            text: true
        }).click(function(event) {
            var max = $(event.target).prevAll("input[name='max']").val();
            var accordion = $(event.target).closest("div.add").prev(".accordion");
            var n_accordion_panes = $(accordion).find(".accordion_unit").length;
            if (n_accordion_panes == max) { // don't need to explicitly check where max="*" b/c this comparison will still be untrue

                $("#confirm_dialog").html("Unable to add; this would create more than the maxium number of instances.");
                $("#confirm_dialog").dialog("option", {
                    title: "add",
                    dialogClass: "no_close",
                    height: 200,
                    width: 400,
                    buttons: {
                        ok: function () {
                            $(this).dialog("close");
                        }
                    }
                }).dialog("open");

            }
            else {

                var dynamic_formset_add_button = $(event.target).closest("div.add").prev(".accordion").find(".add-row:last");
                $(dynamic_formset_add_button).click();
                // there is function bound to the dynamic-formset add event that will fire after that button is pressed
                // (I don't have to explicitly call add_subform)

            }

        });
    }

    if ( $(element).hasClass("remove")) {
        $(element).button({
            icons: { primary: "ui-icon-circle-minus" },
            text: true
        });
        /* the click event had to move to its own fn ("remove_subform" defined in questionnaire_edit.js) */
    }

    if ( $(element).hasClass("replace")) {
        $(element).button({
            icons: { primary : "ui-icon-refresh" },
            text: true
        }).click(function(event) {

            var accordion = $(event.target).closest(".form").find(".accordion:first");

            $("#confirm_dialog").html("This will remove the current instance and replace it with either an existing or new instance.  You will be unable to undo this operation.  Are you sure you want to continue?");
            $("#confirm_dialog").dialog("option", {
                title: "replace",
                dialogClass: "no_close",
                height: 200,
                width: 400,
                buttons: {
                    yes : function () {

                        var dynamic_formset_remove_button = $(accordion).find(".delete-row:last");
                        $(dynamic_formset_remove_button).click();
                        var dynamic_formset_add_button = $(accordion).find(".add-row:last");
                        $(dynamic_formset_add_button).click();

                        $(this).dialog("close")

                    },
                    no : function() {

                        $(this).dialog("close");

                    }
                }
            }).dialog("open");

        });

    }
}


function dynamic_accordions(element) {
    /* element = $(parent).find(".accordion .accordion_header") */
    /* have to do this in two steps b/c the accordion JQuery method cannot handle any content inbetween accordion panes */
    /* but I need a container for dynamic formsets to be bound to */
    /* so _after_ multiopenaccordion() is called, I stick a div into each pane and bind the formset() method to that div */
    var prefix = $(element).closest(".accordion").attr("name");

    $(element).next().andSelf().wrapAll("<div class='accordion_unit' name='" + prefix + "'></div>");

    var accordion_unit = $(element).closest(".accordion_unit");

    $(accordion_unit).formset({
       prefix : prefix,
       formCssClass : "dynamic_accordion_" + prefix,  /* note that formCssClass is _required_ in this situation */
       /*keepFieldValues : '.multiselect_input',*/  /* this does not seem to be working ?!? (see #395) */
       added : function(row) {
           added_subformset_form(row);
       },
       removed : function(row) {
           removed_subformset_form(row);
       }
   });

}


function accordion_headers(element) {

    /* updates the accordion headers based on the current value of a scientific property */

    $(element).find(".atomic_value").each(function () {
        $(this).trigger("change");
    });
    $(element).find(".ui-multiselect").each(function () {
        console.log("found it");
        var source_name = $(this).prev(".multiselect").attr("name");
        var target_name = source_name.replace("-enumeration_value", "-scientific_property_value");
        $(this).find(".multiselect_header").change(function (event) {
            var source_value = $(this).button("option", "label");
            var target = $("*[name='" + target_name + "']");
            $(target).val(source_value);
        })
    });
}


var enumeration_null_value = "_NONE";
var enumeration_other_value = "_OTHER";

function enumerations(element) {

    /* as w/ standard multiselects, clear any old bindings */
    /* in case this fn gets called when a new subform is added */
    $(element).unbind("multiselect_change");

    var header = $(element).find(".multiselect_header");
    var content = $(element).find(".multiselect_content");

    var other = $(element).siblings("input.other:first");

    $(other).focus(function() {
        /* make enumeration_other selectable by clicking */
        /* _but_ break out of it if you do other things w/ the mouse */
        $(this).one("mouseup", function() {
            $(this).select();
            return false;
        }).select();
    });

    $(element).on("multiselect_change", function(e) {

        /* whenever this element changes, */
        /* check if NONE is selected and if so, de-select everything else (and hide the other widget) */
        /* check if OTHER is selected and if so, show the "other" widget */

        var selected_items = $(content).find("li input:checked");
        var selected_items_values = $(selected_items).map(function () {
            return $(this).val();
        }).get();

        if (selected_items_values.indexOf(enumeration_null_value) != -1) {

            $(selected_items).each(function() {
                if ($(this).val() != enumeration_null_value) {
                    $(this).prop("checked", false);
                    $(this).parents("li:first").removeClass("selected");
                    /* I'll wind up w/ circular events if I simulate clicking */
                    /* $(this).click(); */
                }
            });
            $(other).hide();
            multiselect_set_label(element, header, content);
        }

        else if (selected_items_values.indexOf(enumeration_other_value) != -1) {
            $(other).show();
        }
        else {
            $(other).hide();
        }

    });

    /* force enumeration code to run on initialization */
    $(element).trigger("multiselect_change");
}


function treeviews(element) {

    $(element).dynatree({
        debugLevel      : 0,
        checkbox        : true,
        selectMode      : 3,
        minExpandLevel  : 1,
        activeVisible   : true,
        onActivate      : function(node) {
            show_pane(node.data.key);
        },
        onDeactivate    : function(node) {
            var inactive_pane_id = node.data.key + "_pane";
            var inactive_pane = $("#"+inactive_pane_id);
            $(inactive_pane).hide();
            PREVIOUSLY_SELECTED_TAB = $(inactive_pane).find(".tabs:first").tabs("option","active");
        }
        ,
        onSelect        : function(flag,node) {
            selected_nodes = $(element).dynatree("getSelectedNodes");
            $(element).find(".dynatree-partsel:not(.dynatree-selected)").each(function () {
                var node = $.ui.dynatree.getNode(this);
                selected_nodes.push(node);
            });

            node.tree.visit(function (node) {
                var pane_id = node.data.key + "_pane";
                var pane = $("#" + pane_id);
                if ($.inArray(node, selected_nodes) > -1) {
                    $(pane).removeClass("ui-state-disabled");
                    $(pane).find("input[name$='-active']").prop("checked", true)
                }
                else {
                    $(pane).addClass("ui-state-disabled");
                    $(pane).find("input[name$='-active']").prop("checked", false)
                }
            });
        }
    });

    var root = $(element).dynatree("getRoot");

    root.visit(function(node) {
        var pane_id = node.data.key + "_pane";
        var pane = $("#"+pane_id);

        var active_checkbox = $(pane).find("input[name$='-active']");

//        if ($(active_checkbox).is(":checked")) {
//            console.log(pane_id + " is selected");
//            node.select(true);
//        }
//        else {
//            console.log(pane_id + " is NOT selected");
//        }
//        else {
//            node.select(false);
//        }
//        alert(pane_id + ": " + $(active_checkbox).is(":checked"));
//        node.select($(active_checkbox).is(":checked"));
        node.select(true);
//        node.select(false)
//        node.activate($(active_checkbox).is(":checked"))
        node.expand(true);
    });

    // root is actually a built-in parent of the tree, and not the first item in my list
    // hence this fn call
    var first_child = root.getChildren()[0];
    first_child.activate(true);
}

/* this uses functional closure so that I can re-define it in the "view" template */
/* to ensure is_view is true, which makes properties read-only */

show_pane = function(pane_key, is_view) {

    /* if you don't provide an argument for is_view, set it to false */
    is_view = typeof is_view !== 'undefined' ? is_view : false;

    var pane = $("#" + pane_key + "_pane");

    if (!$(pane).hasClass("loaded")) {

        toastr.info("loading...");

        var project_name = $("#_project_name").val();
        var instance_key = $("#_instance_key").val();
        var section_key = $(pane).attr("data-section-key");

        /* get_form_section_view is the name of the AJAX view to return the particular type of form (new vs existing, edit vs customize) */
        /* for this template; it is set in the template header */
        var url = window.document.location.protocol + "//" + window.document.location.host + "/bak/api/" + project_name + "/" + get_form_section_view + "/" + section_key;

        url += "?session_key=" + instance_key;

        $.ajax({
            url: url,
            type: "GET",
            //async: false,
            success: function (data) {

                $(pane).html(data);
                $(pane).ready(function () {

                    var parent = $(pane);
                    init_widgets(tabs, $(parent).find(".tabs"));
                    init_widgets(helps, $(parent).find(".help_button"));
                    init_widgets(dates, $(parent).find(".datetime, .date"));
                    init_widgets(expanders, $(parent).find(".default, .character"));
                    init_widgets(autocompletes, $(parent).find(".autocomplete"));
                    init_widgets(multiselects, $(parent).find(".multiselect"));
                    init_widgets(buttons, $(parent).find("input.button"));
                    init_widgets(enumerations, $(parent).find(".enumeration"));
                    init_widgets(accordions, $(parent).find(".accordion").not(".fake"));
                    init_widgets(dynamic_accordions, $(parent).find(".accordion .accordion_header"));
                    init_widgets(accordion_buttons, $(parent).find(".subform_toolbar button"));
                    init_widgets(dynamic_accordion_buttons, $(parent).find("button.add, button.remove, button.replace"));
                    init_widgets(fieldsets, $(parent).find(".collapsible_fieldset"));
                    init_widgets(inherits, $(parent).find(".inherited"));
                    init_widgets(readonlies, $(parent).find(".readonly"));
                    init_widgets(changers, $(parent).find(".changer"));  /* forces the change event; for scientific properties, this copies the value to the corresponding header */
                    init_widgets(references, $(parent).find("select.reference"));

                    if (is_view) {
                        /* make things read-only */
                        var standard_properties = $(pane).find(".standard_property");
                        var scientific_properties = $(pane).find("div.scientific_property");
                        var scientific_properties_atomic = $(scientific_properties).find("input, textarea");
                        var scientific_properties_enumeration = $(scientific_properties).find("div.multiselect");
                        var all_properties = standard_properties
                            .add(scientific_properties_atomic)
                            .add(scientific_properties_enumeration);
                        $(all_properties).each(function() {
                            $(this).addClass("ui-state-disabled");  /* .addClass("readonly") */
                            if ($(this).hasClass("multiselect")) {
                                /* TREAT MULTISELECTS DIFFERENTLY... */
                                var header = $(this).find(".multiselect_header");
                                var content = $(this).find(".multiselect_content");
                                $(content).find("li, label, input").each(function() {
                                    /* there are 2 ways to prevent selection: */
                                    /* 1st by blurring focus... */
                                   $(this).focus(function() {
                                       $(this).blur()
                                   });
                                    /* ...2nd by explicitly preventing click propagation */
                                    $(this).click(function (e) {
                                        e.preventDefault();
                                        e.stopPropagation();
                                    });
                                });
                            }

                            else {
                                /* ...THAN ALL OTHER WIDGETS */
                                /* there are 2 ways to prevent selection: */
                                /* 1st by blurring focus... */
                                $(this).focus(function () {
                                    $(this).blur();
                                });
                                /* ...2nd by explicitly preventing click propagation */
                                $(this).click(function (e) {
                                    e.preventDefault();
                                    e.stopPropagation();
                                });
                            }
                        });
                    }

                    /* deal w/ completion icons */

                    init_widgets(completion_icons, $(parent).find("input.required, textarea.required, select.required, div.required"));

                    if (start_with_completion_status_displayed) {
                        /* if this is supposed to display the completion icons, */
                        /* then force the toggle to be checked */
                        /* the first time this fn is run */
                        $("input#completion_toggle").prop("checked", true);
                        start_with_completion_status_displayed = false;
                    }

                    /* hide or show the completion icons */
                    /* TODO: CONVENTIONAL WISDOM SAYS I SHOULD USE .checked INSTEAD OF .is(":checked") */
                    /* TODO: BUT THAT DIDN'T WORK */
                    toggle_completion_icons($("input#completion_toggle").is(":checked"));

                    /* identify the section as loaded for js... */
                    $(pane).addClass("loaded");
                    /* ...and for the django view */
                    $(pane).find("input#id_"+pane_key+"-loaded").prop('checked', true);
                    /* TODO: SINCE I'M LOADING AN ENTIRE PANE, JUST SET ALL LOADED FLAGS TO TRUE */
                    /* TODO: IN THE LONGTERM, THOUGH, I OUGHT TO BE MORE PRECISE HERE */
                    $(pane).find("input[name$='-loaded']").prop("checked", true);

                });
            toastr.clear();
            }
        });

    }
    $(pane).show();
    /* make sure that whichever sub-tab had been selected gets activated once this pane is displayed */
    $(pane).find(".tabs:first").tabs({ "active" : PREVIOUSLY_SELECTED_TAB });
}


function inherits(element) {
    var tree_widget = $("#component_tree").find(".treeview");
    if (!tree_widget.length) {
        /* there is no point of inheriting anything in the absence of a component tree */
        return true
    }
    var tree = $(tree_widget).dynatree("getTree");
    var inheritance_options = $(element).closest(".field").find("div.inheritance_options:first");

    var current_pane = $(element).closest(".pane");
    var current_component_key = $(current_pane).attr("id").replace(/_pane$/, "")
    var current_component_node = tree.getNodeByKey(current_component_key);
    var child_component_keys = [];
    current_component_node.visit(function (node) {
        child_component_keys.push(node.data.key)
    });

    if ($(element).hasClass("multiselect")) {
        $(element).on("multiselect_change", function() {
            if ($(inheritance_options).find(".enable_inheritance").is(":checked")) {

                var source_element_id = $(element).find("div.multiselect_content ul:first").attr("id");
                var target_element_ids_to_inherit_later = new Array();

                $(child_component_keys).each(function () {
                    var child_pane = $(".pane[id='" + this + "_pane']");
                    var target_element_id = source_element_id.replace(current_component_key, this);
                    if ($(child_pane).hasClass("loaded")) {
                        var target_element = $(child_pane).find("#"+target_element_id).closest("div.multiselect");
                        inherit_now(element, target_element);
                    }
                    else {
                        /* the pane has not yet been loaded, so inherit it later */
                        target_element_ids_to_inherit_later.push(target_element_id);
                    }
                });

                if (target_element_ids_to_inherit_later.length) {
                    inherit_later(element, target_element_ids_to_inherit_later);
                }
            }
        });

    }
    else {
        $(element).change(function () {

            if ($(inheritance_options).find(".enable_inheritance").is(":checked")) {

                var source_element_id = $(element).attr("id");
                var target_element_ids_to_inherit_later = new Array();

                $(child_component_keys).each(function () {
                    var child_pane = $(".pane[id='" + this + "_pane']");
                    var target_element_id = source_element_id.replace(current_component_key, this);
                    if ($(child_pane).hasClass("loaded")) {
                        /* the inherited field will exist in the pane, so inherit it now */
                        var target_element = $(child_pane).find("#"+target_element_id);
                        inherit_now(element, target_element);
                    }
                    else {
                        /* the pane has not yet been loaded, so inherit it later */
                        target_element_ids_to_inherit_later.push(target_element_id);
                    }
                });

                if (target_element_ids_to_inherit_later.length) {
                    inherit_later(element, target_element_ids_to_inherit_later)
                }
            }
        });
    }
}


function inherit_now(source_element, target_element) {
    var target_inheritance_options = $(target_element).closest(".field").find("div.inheritance_options:first");
    if ($(target_inheritance_options).find(".enable_inheritance").is(":checked")) {

        /* element_type can be a...
         checkbox input,
         a normal input (including ".other"),
         a select,
         a textarea,
         a single multiselect,
         or a multiple multiselect,
        */

        var element_type = $(source_element).prop("tagName").toLowerCase();

        if (element_type == "input") {
            if ($(source_element).attr("type") == "checkbox") {
                $(target_element).prop("checked", $(source_element).is(":checked"));
            }
            else {
                $(target_element).val($(source_element).val());
                if ($(source_element).hasClass("other")) {
                    $(target_element).show();
                }
            }
        }

        else if (element_type == "select") {
            $(target_element).val($(source_element).val());
        }

        else if (element_type == "textarea") {
            $(target_element).val($(source_element).val())
        }

        else if ($(source_element).hasClass("multiselect")) {
            /* TODO: THIS WILL NOT WORK W/ SORTABLE MULTISELECTS */
            /* TODO: BUT I DON'T THINK THAT FEATURE IS EVER USED */
            /* TODO: SO JUST GET RID OF THAT FEATURE */
            var source_inputs = $(source_element).find("div.multiselect_content li input");
            var target_inputs = $(target_element).find("div.multiselect_content li input");
            $(source_inputs).each(function(input_index, source_input) {
                var target_input = $(target_inputs).eq(input_index);
                $(target_input).prop("checked", $(source_input).prop("checked"))
                $(target_input).trigger("change")
            });
            /* .other is handled above by <input>*/
            /* var other_source_input = $(source_element).siblings("input.other:first") */
            /* var other_target_input = $(target_element).siblings("input.other:first") */
            /* $(other_target_input).val($(other_source_input).val()); */
        }

        else {
            console.log("ERROR: unhandled element type (" + element_type + ") for inheritance.");
        }
    }
}


function inherit_later(source_element, target_element_ids) {
    /* note that target_element_ids is an array; */
    /* I am doing this all-at-once, instead of one-at-a-time */
    /* (as w/ inherit_now), to avoid multiple AJAX calls */

    var inheritance_data = {
        "instance_key": $("input#_instance_key").val()
    };

    var element_type = $(source_element).prop("tagName").toLowerCase();

    if (element_type == "input") {
        if ($(source_element).attr("type") == "checkbox") {
            $(target_element_ids).each(function() {
                inheritance_data[this] = $(source_element).is(":checked");
            });
        }
        else {
            $(target_element_ids).each(function() {
                inheritance_data[this] = $(source_element).val();
            });
        }
    }

    else if (element_type == "select") {
        $(target_element_ids).each(function() {
            inheritance_data[this] = $(source_element).val();
        });
    }

    else if (element_type == "textarea") {
        $(target_element_ids).each(function() {
            inheritance_data[this] = $(source_element).val();
        });
    }

    else if ($(source_element).hasClass("multiselect")) {
        var source_component_key = $(source_element).closest("div.pane").attr("id").replace(/_pane$/, "");
        var component_key_regex = /^id_(.*?)_standard_properties/;
        

        var source_content = $(source_element).find("div.multiselect_content");
        $(source_content).find("li input").each(function() {
            var source_input = this;
            $(target_element_ids).each(function() {
                var target_component_key = component_key_regex.exec(this)[1];
                var target_key = $(source_input).attr("id").replace(source_component_key, target_component_key)
                inheritance_data[target_key] = $(source_input).is(":checked");
            });
        });
    }

    var url = window.document.location.protocol + "//" + window.document.location.host + "/api/add_inheritance_data/";

    $.ajax({
        url: url,
        type: "POST",
        data: inheritance_data,
        cache: false,
        error: function(xhr, status, error) {
            console.log(xhr.responseText + status + error)
        }
    });
}

function add_subform(row) {

    /* this takes place AFTER the form is added */

    var field                   = $(row).closest(".field");
    var accordion               = $(row).closest(".accordion");
    var is_one_to_one           = $(accordion).hasClass("fake");
    var is_one_to_many          = !(is_one_to_one);
    var pane                    = $(row).closest(".pane");
    var accordion_units         = $(accordion).children(".accordion_unit");
    var customizer_id           = $(field).find("input[name='customizer_id']").val();
    var property_id             = $(field).find("input[name='property_id']").val();
    var prefix                  = $(field).find("input[name='prefix']").val();
    var parent_vocabulary_key   = $(pane).find("input[name$='-vocabulary_key']:first").val();
    var parent_component_key    = $(pane).find("input[name$='-component_key']:first").val();
    var n_forms                 = parseInt(accordion_units.length);
    var existing_subforms       = $(accordion_units).find("input[name$='-id']:first").map(function() {
        var removed = $(this).closest(".accordion_content").find(".remove:first input[name$='-DELETE']").val();
        if (!removed) {
            var subform_id = $(this).val();
            if (subform_id != "") {
                return parseInt(subform_id)
            }
        }
    }).get();

    var url = window.document.location.protocol + "//" + window.document.location.host + "/bak/ajax/select_realization/";

    url += "?c=" + customizer_id + "&p=" + prefix + "&n=" + n_forms + "&e=" + existing_subforms + "&p_v_k=" + parent_vocabulary_key + "&p_c_k=" + parent_component_key;
    if (property_id != "") {
        url += "&s=" + property_id;
    }

    var old_prefix = $(accordion).attr("name");
    /* TODO: DOUBLE-CHECK THAT THIS IS ALWAYS CREATING A NEWFORM W/ ID=0 */
    /*old_prefix += "-" + (n_forms - 2);*/
    old_prefix += "-" + "0";

    $.ajax({
        url     : url,
        type    : "GET",
        cache   : false,
        error   : function(xhr,status,error) {
            console.log(xhr.responseText + status + error);
        },
        success : function(data,status,xhr) {

            var status_code = xhr.status;

            if (status_code == 200 ) {

                var parsed_data = $.parseJSON(data);
                var new_prefix = parsed_data.prefix;
                var new_label = parsed_data.label;

                /* rename ids and names */
                update_field_names(row, old_prefix, new_prefix);
                /* insert data */
                populate_form(row, parsed_data);
                /* make sure that all 'loaded' fields are set to true */
                $(row).find("input[name$='-loaded']").prop("checked", true);
                /* update label */
                $(row).find(".accordion_header:first .label").html(new_label);
                /* the copy fn copies over all classes; I need to remove the ones that prevent re-setting js */
                clear_js_widgets(row);

                /* initialize JQuery widgets */
                $(row).ready(function () {

                    init_widgets(completion_icons, $(row).find("input.required, textarea.required, select.required, div.required"));

                    if (is_one_to_many) {
                        init_widgets_on_show(fieldsets, $(row).find(".collapsible_fieldset"))
                        init_widgets_on_show(helps, $(row).find(".help_button"));
                        init_widgets_on_show(readonlies, $(row).find(".readonly"));
                        init_widgets_on_show(dates, $(row).find(".datetime,.date"));
                        init_widgets_on_show(accordions, $(row).find(".accordion").not(".fake"));
                        init_widgets_on_show(dynamic_accordions, $(row).find(".accordion .accordion_header"));
                        init_widgets_on_show(accordion_buttons, $(row).find(".subform_toolbar button"));
                        init_widgets_on_show(dynamic_accordion_buttons, $(row).find("button.add,button.remove,button.replace"));
                        init_widgets_on_show(enumerations, $(row).find(".enumeration"));
                        init_widgets_on_show(multiselects, $(row).find(".multiselect"));
                        init_widgets_on_show(autocompletes, $(row).find(".autocomplete"));
                        init_widgets_on_show(enablers, $(row).find(".enabler"));
                    }

                    else if (is_one_to_one) {
                        init_widgets(fieldsets, $(row).find(".collapsible_fieldset"))
                        init_widgets(helps, $(row).find(".help_button"));
                        init_widgets(readonlies, $(row).find(".readonly"));
                        init_widgets(dates, $(row).find(".datetime,.date"));
                        init_widgets(accordions, $(row).find(".accordion").not(".fake"));
                        init_widgets(dynamic_accordions, $(row).find(".accordion .accordion_header"));
                        init_widgets(accordion_buttons, $(row).find(".subform_toolbar button"));
                        init_widgets(dynamic_accordion_buttons, $(row).find("button.add,button.remove,button.replace"));
                        init_widgets(enumerations, $(row).find(".enumeration"));
                        init_widgets(multiselects, $(row).find(".multiselect"));
                        init_widgets(autocompletes, $(row).find(".autocomplete"));
                        init_widgets(enablers, $(row).find(".enabler"));
                    }

                    else {
                        console.log("unable to determine if this is a one-to-one or a one-to-many subform; cannot initialize jquery widgets");
                    }
                });

            }

        }
    });
}

function add_subform_old(row) {

    /* this takes place AFTER the form is added */
    
    var field                   = $(row).closest(".field");
    var accordion               = $(row).closest(".accordion");
    var is_one_to_one           = $(accordion).hasClass("fake");
    var is_one_to_many          = !(is_one_to_one);
    var pane                    = $(row).closest(".pane");
    var accordion_units         = $(accordion).children(".accordion_unit");
    var customizer_id           = $(field).find("input[name='customizer_id']").val();
    var property_id             = $(field).find("input[name='property_id']").val();
    var prefix                  = $(field).find("input[name='prefix']").val();
    var parent_vocabulary_key   = $(pane).find("input[name$='-vocabulary_key']:first").val();
    var parent_component_key    = $(pane).find("input[name$='-component_key']:first").val();
    var n_forms                 = parseInt(accordion_units.length);
    var existing_subforms       = $(accordion_units).find("input[name$='-id']:first").map(function() {
        var removed = $(this).closest(".accordion_content").find(".remove:first input[name$='-DELETE']").val();
        if (!removed) {
            var subform_id = $(this).val();
            if (subform_id != "") {
                return parseInt(subform_id)
            }
        }
    }).get();

    var url = window.document.location.protocol + "//" + window.document.location.host + "/ajax/select_realization/";
    url += "?c=" + customizer_id + "&p=" + prefix + "&n=" + n_forms + "&e=" + existing_subforms + "&p_v_k=" + parent_vocabulary_key + "&p_c_k=" + parent_component_key;
    if (property_id != "") {
        url += "&s=" + property_id;
    }

    var old_prefix = $(accordion).attr("name");
    /* TODO: DOUBLE-CHECK THAT THIS IS ALWAYS CREATING A NEWFORM W/ ID=0 */
    /*old_prefix += "-" + (n_forms - 2);*/
    old_prefix += "-" + "0";

    var add_subform_dialog = $("#add_dialog");

    $.ajax({
        url     : url,
        type    : "GET",
        cache   : false,
        success : function(data) {
            $(add_subform_dialog).html(data);
            $(add_subform_dialog).dialog("option",{
                height      : 300,
                width       : 600,
                dialogClass : "no_close",
                title       : "Select an instance to add",
                open : function() {
                    // apply all of the JQuery code to _this_ dialog
                    var parent = $(add_subform_dialog);
                    // the addition of the 'true' attribute forces initialization,
                    // even if this dialog is opened multiple times
                    init_widgets(buttons, $(parent).find("input.button"), true);
                    init_widgets(fieldsets, $(parent).find(".collapsible_fieldset"), true);
                    init_widgets(helps, $(parent).find(".help_button"), true);
                    init_widgets(multiselects, $(parent).find(".multiselect"), true);
                },

                buttons : [
                    {
                        text : "ok",
                        click : function() {

                            var add_subform_data = $(this).find("#select_realization_form").serialize();
                            $.ajax({
                                url     : url,
                                type    : "POST",  // (POST mimics submit)
                                data    : add_subform_data,
                                cache   : false,
                                error   : function(xhr,status,error) {
                                    console.log(xhr.responseText + status + error);
                                },
                                success : function(data,status,xhr) {

                                    var status_code = xhr.status;

                                    if (status_code == 200 ) {

                                        var parsed_data = $.parseJSON(data);
                                        var new_prefix = parsed_data.prefix;
                                        var new_label = parsed_data.label;

                                        /* rename ids and names */
                                        update_field_names(row,old_prefix,new_prefix);
                                        /* insert data */
                                        populate_form(row,parsed_data);
                                        /* make sure that all 'loaded' fields are set to true */
                                        $(row).find("input[name$='-loaded']").prop("checked", true);
                                        /* update label */
                                        $(row).find(".accordion_header:first .label").html(new_label);

                                        /* initialize JQuery widgets */
                                        $(row).ready(function() {

                                            if (is_one_to_many) {
                                                init_widgets_on_show(fieldsets, $(row).find(".collapsible_fieldset"))
                                                init_widgets_on_show(helps, $(row).find(".help_button"));
                                                init_widgets_on_show(readonlies, $(row).find(".readonly"));
                                                init_widgets_on_show(dates, $(row).find(".datetime,.date"));
                                                init_widgets_on_show(accordions, $(row).find(".accordion").not(".fake"));
                                                init_widgets_on_show(dynamic_accordions, $(row).find(".accordion .accordion_header"));
                                                init_widgets_on_show(accordion_buttons, $(row).find(".subform_toolbar button"));
                                                init_widgets_on_show(dynamic_accordion_buttons, $(row).find("button.add,button.remove,button.replace"));
                                                init_widgets_on_show(multiselects, $(row).find(".multiselect"));
                                                init_widgets_on_show(enumerations, $(row).find(".enumeration"));
                                                init_widgets_on_show(autocompletes, $(row).find(".autocomplete"));
                                                init_widgets_on_show(enablers, $(row).find(".enabler"));
                                            }

                                            else if (is_one_to_one) {
                                                init_widgets(fieldsets, $(row).find(".collapsible_fieldset"))
                                                init_widgets(helps, $(row).find(".help_button"));
                                                init_widgets(readonlies, $(row).find(".readonly"));
                                                init_widgets(dates, $(row).find(".datetime,.date"));
                                                init_widgets(accordions, $(row).find(".accordion").not(".fake"));
                                                init_widgets(dynamic_accordions, $(row).find(".accordion .accordion_header"));
                                                init_widgets(accordion_buttons, $(row).find(".subform_toolbar button"));
                                                init_widgets(dynamic_accordion_buttons, $(row).find("button.add,button.remove,button.replace"));
                                                init_widgets(multiselects, $(row).find(".multiselect"));
                                                init_widgets(enumerations, $(row).find(".enumeration"));
                                                init_widgets(autocompletes, $(row).find(".autocomplete"));
                                                init_widgets(enablers, $(row).find(".enabler"));
                                            }

                                            else {
                                                console.log("unable to determine if this is a one-to-one or a one-to-many subform; cannot initialize jquery widgets");
                                            }



                                        });

                                        $(add_subform_dialog).dialog("close");

                                    }
                                    else {

                                        /*
                                         note - do not use a status code of 400 for form valiation errors
                                         that will be routed to the "error" event above
                                         instead use some valid success code other than 200 (202, for example)
                                        */

                                        var msg = xhr.getResponseHeader("msg");
                                        var msg_dialog = $(document.createElement("div"));
                                        msg_dialog.html(msg);
                                        msg_dialog.dialog({
                                            modal: true,
                                            title : "error",
                                            hide: "explode",
                                            height: 200,
                                            width: 400,
                                            // I'm only ever showing a dialog box if there was an error in the POST
                                            // TODO: ENSURE THE ERROR CLASS PROPAGATES TO ALL CHILD NODES?
                                            dialogClass: "no_close ui-state-error",
                                            buttons: {
                                                OK: function () {
                                                    $(this).dialog("close");
                                                }
                                            }
                                        });

                                        $(add_subform_dialog).html(data);
                                        // re-apply all of the JQuery code to _this_ dialog
                                        var parent = $(add_subform_dialog);
                                        // the addition of the 'true' attribute forces initialization,
                                        // even if this dialog is opened multiple times
                                        init_widgets(buttons, $(parent).find("input.button"), true);
                                        init_widgets(fieldsets, $(parent).find(".collapsible_fieldset"), true);
                                        init_widgets(multiselects, $(parent).find(".multiselect"), true);
                                        init_widgets(helps, $(parent).find(".help_button"), true);
                                    }
                                }
                            })
                        }
                    },
                    {
                        text : "cancel",
                        click : function() {

                            var dynamic_formset_remove_button = $(row).find(".delete-row:first");
                            $(dynamic_formset_remove_button).click();

                            $(add_subform_dialog).dialog("close");
                        }
                    }
                ],
                close   : function() {
                    $(this).dialog("close");
                }
            }).dialog("open");
        }
    });
}


function remove_subform(remove_button) {

    /* this takes place BEFORE the form is removed */

    var min = $(remove_button).prevAll("input[name='min']").val();
    var accordion = $(remove_button).closest(".accordion");
    var n_accordion_panes = $(accordion).find(".accordion_unit").length;
    if (n_accordion_panes == min) {

        $("#confirm_dialog").html("Unable to remove; this would result in less than the minumum number of instances.");
        $("#confirm_dialog").dialog("option", {
            title: "remove",
            dialogClass: "no_close",
            height: 200,
            width: 400,
            buttons: {
                ok: function () {
                    $(this).dialog("close");
                }
            }
        }).dialog("open");

    }
    else {

        $("#confirm_dialog").html("Removing this will delete the relationship but not the underlying instance.  Do you wish to continue?.");
        $("#confirm_dialog").dialog("option", {
            title: "remove",
            dialogClass: "no_close",
            height: 200,
            width: 400,
            buttons: {
                yes: function () {
                    var dynamic_formset_remove_button = $(remove_button).closest(".accordion_content").next(".delete-row:first");
                    $(dynamic_formset_remove_button).click();
                    // there is function bound to the dynamic-formset remove event that will fire after that button is pressed
                    // (I don't have to explicitly call anything)
                    $(this).dialog("close")
                },
                no: function () {
                    $(this).dialog("close")
                }
            }
        }).dialog("open");
    }
}


function added_subformset_form(row) {
    add_subform(row);
}


function removed_subformset_form(row) {
    /* don't have to do anything else */
    /* hooray */
}

/* a bunch of code for dealing w/ completion */

var start_with_completion_status_displayed = false;


function set_initial_treeview_completion_icons(treeview, initial_completion_status) {

    var tree = $(treeview).dynatree("getTree");
    $.each(initial_completion_status, function(key, status) {
        var node = tree.getNodeByKey(key);
        var completion_icon = $(node.li).find("span.completion_icon:first span.ui-icon");
        /* don't worry about tracking n_complete & n_total as below */
        /* this fn just sets the initial state based on models */
        /* the current state based on forms gets set upon loading */
        if (status) {
            $(completion_icon).addClass("complete");
            $(completion_icon).removeClass("incomplete");
        }
        else {
            $(completion_icon).removeClass("complete");
            $(completion_icon).addClass("incomplete");
        }
    });
}


function is_complete(element) {
    if ($(element).hasClass("multiselect")) {
        /* treat enumerations slightly differently */
        /* (b/c they use a custom JQuery widget) */
        var selected_items = get_multiselect_value(element);
        var num_selected_items = selected_items.length;
        return (num_selected_items > 0);
    }
    else {
        var value = $(element).val();
        var type = $(element).prop("tagName");
        if (type == "SELECT") {
            if (value) {
                return Boolean(value);
            }
            else {
                return false;
            }
        }
        else {
            if (value) {
                return Boolean(value.trim());
            }
            else {
                return false;
            }
        }
    }
}


function completion_icons(element) {

    var is_multiselect = $(element).hasClass("multiselect");
    var type = $(element).prop("tagName");

    /* get the completion icon for this particular tab / category */
    var tab_id = $(element).closest("div.tab_content").parent("div").attr("id");
    var tab_header = $(element).closest("div.tabs").find("a[href='#" + tab_id + "']");
    var tab_completion_icon =$(tab_header).find(".completion_icon:first")

    /* and get the completion icon for this particualr pane / component */
    var pane = $(element).parents("div.pane");
    var pane_completion_icon = $(pane).find(".completion_icon:first");

    /* and put them together */
    var completion_icons = $(pane_completion_icon).add(tab_completion_icon).add(treeview_completion_icon);

    /* oh, and get the completion icon for the corresopnding node in the treeview */
    /* (iff it exists) */
    var treeview = $("div#component_tree div.treeview");
    if (treeview.length) {
        var pane_key = $(pane).attr("id");
        var component_key = pane_key.substr(0, pane_key.length - 5);
        /* (5 is the length of the string "_pane") */
        var tree = $(treeview).dynatree("getTree");
        var node = tree.getNodeByKey(component_key);
        var treeview_completion_icon = $(node.li).find("span.completion_icon:first");

        completion_icons = $(completion_icons).add(treeview_completion_icon);
    }

    $(completion_icons).each(function() {

        var completion_icon = this;
        var icon = $(completion_icon).find("span.ui-icon");

        var n_total_input = $(completion_icon).find("input[name='n_total']");
        $(n_total_input).val(function(i, old_val) {
            return ++old_val;
        });
        var n_total = $(n_total_input).val();

        var n_complete_input = $(this).find("input[name='n_complete']");
        if (is_complete(element)) {
            $(n_complete_input).val(function(i, old_val) {
                return ++old_val;
            });
        }
        var n_complete = $(n_complete_input).val();

        if (n_total == n_complete) {
            $(icon).addClass("complete");
            $(icon).removeClass("incomplete");
        }
        else {
            $(icon).removeClass("complete");
            $(icon).addClass("incomplete");
        }
    });

    if (is_multiselect) {
        /* treat enumerations slightly differently */
        /* (b/c they use a custom JQuery widget) */
        $(element).find("button:first").on("focus", function() {
            var selected_items = get_multiselect_value(element);
            element.old_value = selected_items.join(", ");
        });
    }
    else {
        if (type=="SELECT") {
            var selected_options = $(element).find(":selected").map(function() {
               return $(this).attr("value");
            }).get();
            element.old_value = selected_options.join(", ")
        }
        else {
            $(element).on("focus", function() {
                element.old_value = $(element).val();
            });
        }
    }

    $(element).on("change", function() {
        var old_value = element.old_value;
        if (is_multiselect) {
            /* treat enumerations slightly differently */
            /* (b/c they use a custom JQuery widget) */
            var selected_items = get_multiselect_value(element);
            var new_value = selected_items.join(", ");
        }
        else {
            if (type == "SELECT") {
                var selected_options = $(element).find(":selected").map(function() {
                    return $(this).attr("value");
                }).get();
                var new_value = selected_options.join(", ");
            }
            else {
                var new_value = $(element).val();
            }
        }
        /* if there was an old_value and there is now no new_value */
        /* or if there was no old_value and there is now a new_value */
        /* then adjust the number of completed fields accordingly */
        if ((old_value || new_value) && !(old_value && new_value)) {
            var complete = is_complete(element);
            $(completion_icons).each(function() {
                var completion_icon = this;
                var icon = $(completion_icon).find("span.ui-icon");
                var n_total_input = $(completion_icon).find("input[name='n_total']");
                var n_complete_input = $(completion_icon).find("input[name='n_complete']");
                $(n_complete_input).val(function (i, old_val) {
                    if (complete) {
                        return ++old_val;
                    }
                    else {
                        return --old_val;
                    }
                });
                var n_total = $(n_total_input).val();
                var n_complete = $(n_complete_input).val();
                if (n_total == n_complete) {
                    $(icon).addClass("complete");
                    $(icon).removeClass("incomplete");
                }
                else {
                    $(icon).removeClass("complete");
                    $(icon).addClass("incomplete");
                }
            });
        }
        element.old_value = new_value;
    });
}


function toggle_completion_icons(checked) {

    $(".completion_icon").each(function() {
        /* show or hide the "complete completion_icon" section */
        /* the icon itself is displayed conditionally via CSS */
        /* based on the "complete" or "incomplete" class set above */
        if (checked) {
            $(this).show();
        }
        else {
            $(this).hide();
        }
    });
}

/* publishing */

function publish() {
    var instance_key = $("#_instance_key").val();
    var url = window.document.location.protocol + "//" + window.document.location.host + "/api/publish/";
    $.ajax({
        url: url,
        type: "POST",
        cache: false,
        data: { "instance_key": instance_key},
        success: function (data, status, xhr) {
            var msg = xhr.getResponseHeader("msg");
            var msg_dialog = $(document.createElement("div"));
            msg_dialog.html(msg);
            msg_dialog.dialog({
                modal: true,
                hide: "explode",
                height: 200,
                width: 400,
                dialogClass: "no_close",
                buttons: {
                    OK: function () {
                        $(this).dialog("close");
                    }
                }
            });

            var status_code = xhr.status;

            if (status_code != 200) {
                var completion_toggle = $("input#completion_toggle");
                if (! $(completion_toggle).prop("checked")) {
                    $(completion_toggle).click();
                }
            }

        }
    });
}