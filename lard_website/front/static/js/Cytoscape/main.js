function initCytoscape(data) {
    var cy = window.cy = cytoscape({

        container: document.getElementById("cy"),


        layout: {
            name: "grid",
            rows: 2,
            cols: 2
        },

        style: [
            {
                selector: "node",
                style: {
                    "content": "data(name)",
                    "shape": "square",
                    'color': 'black'
                }
            },
            {
                selector: 'node:selected',
                style: {
                    'background-color': '#2E86C1',
                }
            },


            {
                selector: "edge",
                style: {
                    "curve-style": "bezier",
                    "content": "data(name)",
                    "target-arrow-shape": "triangle",
                    'line-color': '#009688',
                    'target-arrow-color': '#009688'

                }
            },
            {
                selector: 'edge:selected',
                style: {
                    'line-color': '#2E86C1'
                }
            },

            // some style for the extension

            {
                selector: ".eh-handle",
                style: {
                    "background-color": "red",
                    "width": 12,
                    "height": 12,
                    "shape": "ellipse",
                    "overlay-opacity": 0,
                    "border-width": 12, // makes the handle easier to hit
                    "border-opacity": 0
                }
            },

            {
                selector: ".eh-hover",
                style: {
                    "background-color": "red"
                }
            },

            {
                selector: ".eh-source",
                style: {
                    "border-width": 2,
                    "border-color": "red"
                }
            },

            {
                selector: ".eh-target",
                style: {
                    "border-width": 2,
                    "border-color": "red"
                }
            },

            {
                selector: ".eh-preview, .eh-ghost-edge",
                style: {
                    "background-color": "red",
                    "line-color": "red",
                    "target-arrow-color": "red",
                    "source-arrow-color": "red"
                }
            },

            {
                selector: ".eh-ghost-edge.eh-preview-active",
                style: {
                    "opacity": 0
                }
            }
        ],

        elements: data
    });

    let defaults = {
        preview: true,
        hoverDelay: 150,
        handleNodes: "node",
        snap: false,
        snapThreshold: 50,
        snapFrequency: 15,
        noEdgeEventsInDraw: false,
        disableBrowserGestures: true,

        ghostEdgeParams: function () {

            return {};
        },

    };

    var eh = cy.edgehandles(defaults);
    let menu = cy.cxtmenu(defaults);
    var supp;

    cy.cxtmenu({
        selector: 'node, edge',

        commands: [

            {
                content: '<span class="fa fa-remove fa-2x" style="color: #c53a3a;"></span>',
                select: function (ele) {
                    supp = cy.remove(ele);
                    createArray(cy);
                },
                activeFillColor: 'rgba(255,0,0,0.2)',
            },
            {
                content: '<span class="fa fa-edit fa-2x" ></span>',
                select: function (ele) {
                    if (ele.isNode()) {
                        var donnees;
                        for (var dat in ele.data()["data"]) {
                            donnees = ele.data()["data"][dat];
                        }
                        jQuery('#modalDiv').load("/pipelines/" + pipelineName + "/edit/block/" + ele.data()["name"] + "/" + ele.id(), function (result) {
                            jQuery("#pipelineModal").modal({show: true});
                        });
                    }
                    if (ele.isEdge()) {
                        var old_name = "";
                        if (ele.data()["old_name"] !== "undefined") {
                            old_name = ele.data()["old_name"];
                        }
                        var new_name = "";
                        if (ele.data()["new_name"] !== "undefined") {
                            new_name = ele.data()["new_name"];
                        }
                        jQuery('#modalDiv').load("/pipelines/" + pipelineName + "/edit/edge/" + cy.filter('[id = "' + ele.data()["source"] + '"]').data()["name"]
                            + "/" + cy.filter('[id = "' + ele.data()["target"] + '"]').data()["name"] + "/" + ele.id() + "/" + old_name + "/" + new_name, function (result) {
                            jQuery("#pipelineModal").modal({show: true});

                        });
                    }

                }
            }
        ]
    });

    cy.cxtmenu({
        selector: 'core',

        commands: [
            {
                content: '<span class="fa fa-plus fa-2x" ></span>',
                select: function () {
                    jQuery('#collapseExample').collapse('toggle');
                }
            },
            {
                content: '<span class="fa fa-undo fa-2x" ></span>',
                select: function () {
                    supp.restore();
                    createArray(cy);
                }
            }
        ]
    });


    //Permet de faire la création du node
    document.querySelector("#create").addEventListener("click", function () {

        //Récupération du nom
        var nom = document.getElementById("name").value;
        var type = document.getElementById("type").value;
        cy.add({
            group: "nodes",
            data: {
                "name": nom,
                "id": nom,
                "type": type,
                "data": {},
                "on_launch": false
            },
            position: {
                x: Math.floor(Math.random() * (cy.width() - 500)) + 300,
                y: Math.floor(Math.random() * (cy.height() - 500)) + 100
            }
        });


        cy.pan();
        cy.center();
        createArray(cy);
    });


    //Permet de delete nodes et edges avec "Suppr"
    document.addEventListener("keydown", function (e) {
        if (e.keyCode === 46) {
            supp = cy.remove(":selected");
            createArray(cy);
        }

        if (e.keyCode === 27) {
            jQuery('#collapseExample').collapse('hide');
            createArray(cy);
        }
        if (e.ctrlKey && e.keyCode === 90) {
            supp.restore();
            createArray(cy);

        }
        if (e.ctrlKey && (e.which === 83)) {
            e.preventDefault();
            createArray(cy);
            jQuery('#runButton').trigger('click');

        }

    }, false);

    //Event lors de la fin de la création d"un edge
    cy.on("ehcomplete", (event, sourceNode, targetNode) => {
        createArray(cy);
    });

    cy.elements().forEach(function (elem) {
        console.log(elem.data());
    });
}

function edit(cy, param) {
    var dataNode = cy.$('#' + param[0]).data();
    dataNode["data"] = param[1];
    dataNode["on_launch"] = param[2];
    dataNode["data_ready"] = {};
    createArray(cy);
}

function editEdge(cy, param) {
    console.log(param);
    var dataNode = cy.$('#' + param[0]).data();
    dataNode["old_name"] = param[1];
    dataNode["new_name"] = param[2];
    createArray(cy);
}

function createArray(cy) {
    var jsonCytoscape = {};
    var array_nodes = [];
    var array_edges = [];
    cy.elements().forEach(function (elem) {
        console.log(elem.data());
        var dict_data = {};
        var dict_data_edge = {};

        if (elem.isNode()) {

            if (elem.data().id.length <= 20) {

                dict_data["data"] = elem.data();

                dict_data["block_data"] = {
                    "data": elem.data()["data"],
                    "data_ready": {},
                    "on_launch": elem.data()["on_launch"]
                };
                array_nodes.push(dict_data);

            }
        }
        if (elem.isEdge()) {
            if (elem.data().target.length <= 20) {
                dict_data_edge["data"] = elem.data();
                array_edges.push(dict_data_edge);
            }
        }
    });
    jsonCytoscape["edges"] = array_edges;
    jsonCytoscape["nodes"] = array_nodes;

    console.log(jsonCytoscape);
    updatePipeline(jsonCytoscape);
}

function updatePipeline(data) {
    jQuery.ajax({
        type: "POST",
        url: "/api/piplines/update",
        dataType: "json",
        traditional: true,
        data: {'name': pipelineName, 'pipeline': JSON.stringify(data)},
        success: function (code, statut) {
            console.log(pipelineName + " updated");
        },
        error: function (code, statut) {
            console.log("Error during " + pipelineName + " update");
        }
    });
}