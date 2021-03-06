var edge_wait = false;
var event_wait, sourceNode_wait, targetNode_wait;

function initCytoscape(data) {
    var cy = window.cy = cytoscape({

        container: document.getElementById("cy"),

        layout: {
            name: 'cose',
            idealEdgeLength: 10,
            nodeOverlap: 20,
            refresh: 20,
            fit: true,
            padding: 30,
            randomize: false,
            componentSpacing: 100,
            nodeRepulsion: 20000000,
            edgeElasticity: 100,
            nestingFactor: 5,
            gravity: 800,
            numIter: 1000,
            initialTemp: 200,
            coolingFactor: 0.95,
            minTemp: 1.0
        },
        style: [
            {
                selector: "node[?on_launch]",
                style: {
                    "background-color": "#28a745"
                }
            },
            {
                selector: 'node[type = "Output"]',
                style: {
                    "background-color": "#17a2b8"
                }
            },
            {
                selector: "node",
                style: {
                    "content": "data(name)",
                    "shape": "round-rectangle",
                    'color': 'black',
                    'text-outline-width': 1,
                    'text-outline-color': '#f1f2f7'
                }
            },
            {
                selector: 'node:selected',
                style: {
                    'background-color': '#266fc1',
                }
            },
            {
                selector: "edge",
                style: {
                    "curve-style": "bezier",
                    "content": "data(name)",
                    "target-arrow-shape": "triangle",
                    'line-color': '#009688',
                    'target-arrow-color': '#009688',
                    'arrow-scale': 2,
                    'line-style': 'dashed',
                    'line-dash-pattern': [7, 4]
                }
            },
            {
                selector: 'edge:selected',
                style: {
                    'line-color': '#266fc1',
                    'target-arrow-color': '#266fc1'
                }
            },
            {
                selector: ".eh-handle",
                style: {
                    "background-color": "red",
                    "width": 12,
                    "height": 12,
                    "shape": "ellipse",
                    "overlay-opacity": 0,
                    "border-width": 12,
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
            },
            {
                selector: ".highlighted",
                style: {
                    'background-color': '#007bff',
                    'line-color': '#007bff',
                    'target-arrow-color': '#007bff',
                    'transition-property': 'background-color, line-color, target-arrow-color',
                    'transition-duration': '0.5s'
                }
            },
            {
                selector: ".error",
                style: {
                    'background-color': '#bd2130',
                    'line-color': '#bd2130',
                    'target-arrow-color': '#bd2130',
                    'transition-property': 'background-color, line-color, target-arrow-color',
                    'transition-duration': '0.5s'
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
    var supp;

    cy.cxtmenu({
            selector: 'node',
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

                            jQuery('#modalDiv').load("/pipelines/" + pipelineName + "/edit/block/" + ele.data()["name"] + "/" + ele.id(), function (result) {
                                jQuery("#pipelineModal").modal({show: true});
                            });
                        }
                    }
                },
                {
                    content: '<span class="fa fa-info fa-2x"></span>',
                    select: function (ele) {
                        if (ele.isNode()) {
                            jQuery('#modalDiv').load("/pipelines/" + pipelineName + "/info/block/" + ele.data()["name"] + "/" + ele.id(), function (result) {
                                jQuery("#pipelineModal").modal({show: true});
                            });
                        }
                    },
                    activeFillColor:
                        'rgba(255,0,0,0.2)',
                }
            ]
        }
    );

    cy.cxtmenu({
            selector: 'edge',
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
        }
    );


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

    document.querySelector("#reload").addEventListener("click", function () {
        cy.center();
        cy.pan();
        cy.fit();
        clearStyle(cy);
    });

    document.querySelector("#create").addEventListener("click", function () {
        var nom = document.getElementById("name").value;
        var type = document.getElementById("type").value;
        var launch = document.getElementById("onLaunchCreate").checked;
        cy.add({
            group: "nodes",
            data: {
                "name": nom,
                "id": nom,
                "type": type,
                "data": {},
                "on_launch": launch
            },
            position: {
                x: Math.floor((Math.random() * 600) + 550),
                y: Math.floor((Math.random() * 700) + 500)
            }
        });
        cy.resize();
        cy.fit();
        createArray(cy);
        if (cy.filter('node[name = "Han Solo"]').data()) {
            document.getElementById('han').style.display = 'block';
            document.getElementById('brand').style.display = 'none';
        }
        if (cy.filter('node[name = "Raynal"]').data()) {
            document.getElementById('rayn').style.display = 'block';
            document.getElementById('brand').style.display = 'none';
        }
    });

    document.querySelector("#import").addEventListener("click", function () {
        let toMerge = document.getElementById("pipeline").value;
        jQuery("#loader").fadeIn(0);
        jQuery.ajax({
            type: "POST",
            url: "/pipelines/" + pipelineName + "/merge",
            dataType: "json",
            traditional: true,
            data: {'to_merge': toMerge},
            success: function (data, statut) {
                console.log(data);
                console.log(statut);
                initCytoscape(data);
                console.log("Merge " + pipelineName + " and " + toMerge);
            },
            error: function (code, statut) {
                console.log("Error during " + pipelineName + " merge");
            }
        });

        jQuery("#loader").fadeOut();
    });

    document.addEventListener("keydown", function (e) {
        if (e.keyCode === 46) {
            supp = cy.remove(":selected");
            createArray(cy);
        }

        if (e.keyCode === 27) {
            jQuery('#collapseExample').collapse('hide');
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

        if (e.keyCode === 13) {
            jQuery('#collapseExample').collapse('toggle');
        }
    }, false);

    cy.on("ehcomplete", (event, sourceNode, targetNode) => {
        createArray(cy);
        edge_wait = true;
        event_wait = event;
        sourceNode_wait = sourceNode;
        targetNode_wait = targetNode;
    });

    cy.elements().forEach(function (elem) {
        console.log(elem.data());
    });

}

function highlight(source, target, old_name, new_name) {
    let edge;
    if (old_name && new_name) {
        edge = cy.filter('edge[source = "' + source + '"][target = "' + target + '"][old_name = "' + old_name + '"][new_name = "' + new_name + '"]');
    } else {
        edge = cy.filter('edge[source = "' + source + '"][target = "' + target + '"]');
    }
    edge.addClass('highlighted');
}

function highlightNode(name) {
    let node;
    node = cy.filter('node[name = "' + name + '"]');
    node.addClass('highlighted');
}

function highlightError(name) {
    let node;
    node = cy.filter('node[name = "' + name + '"]');
    node.addClass('error');
}

function edit(cy, param) {
    var dataNode = cy.$('#' + param[0]).data();

    for (var key in param[1]) {
        if (param[1][key] == "None") {
            param[1][key] = null;
        }
        if (param[1][key] == "") {
            param[1][key] = null;
        }
    }

    dataNode["data"] = param[1];
    dataNode["on_launch"] = param[2];
    dataNode["data_ready"] = {};
    createArray(cy);
}

function clearStyle(cy) {
    cy.elements().forEach(function (elem) {
        elem.removeClass('highlighted');
        elem.removeClass('error');
    });

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
    cy.style().update();
    updatePipeline(jsonCytoscape);
}


function updatePipeline(data) {
    if (userIsOwner) {
        jQuery.ajax({
            type: "POST",
            url: "/api/pipelines/update",
            dataType: "json",
            traditional: true,
            data: {'name': pipelineName, 'pipeline': JSON.stringify(data)},
            success: function (code, statut) {
                console.log(pipelineName + " updated");
                if (edge_wait) {
                    openModal()
                }
            },
            error: function (code, statut) {
                console.log("Error during " + pipelineName + " update");
            }
        });
    }
}

function openModal() {
    var edge;
    cy.elements().forEach(function (elem) {
        if (elem.isEdge()) {
            if (elem.data().target === targetNode_wait.data()["name"] && elem.data().source === sourceNode_wait.data()["name"]) {
                edge = elem;
            }
        }
    });
    var old_name = "image";
    var new_name = "image";
    jQuery('#modalDiv').load("/pipelines/" + pipelineName + "/edit/edge/" + sourceNode_wait.data()["name"]
        + "/" + targetNode_wait.data()["name"] + "/" + edge.id() + "/" + old_name + "/" + new_name, function (result) {
        jQuery("#pipelineModal").modal({show: true});

    });
    edge_wait = false;
}

var script = document.createElement("script"),
    body = document.getElementsByTagName("body")[0],
    toggle = false;
script.type = "text/javascript";
script.addEventListener("load", function () {
    new KonamiCode(function () {
        if (toggle) {
            toggle = false;
            body.style = "overflow-x: hidden;transition: transform 2s ease;transform: rotate(0deg)";
        } else {
            toggle = true;
            body.style = "overflow-x: hidden;transition: transform 2s ease;transform: rotate(180deg)";
        }
    });
});
script.src = "https://cdn.rawgit.com/Haeresis/konami-code-js/master/src/konami-code.js";
body.appendChild(script);