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
                }
            },

            {
                selector: "edge",
                style: {
                    "curve-style": "bezier",
                    "content": "data(name)",
                    "target-arrow-shape": "triangle"
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
        preview: true, // whether to show added edges preview before releasing selection
        hoverDelay: 150, // time spent hovering over a target node before it is considered selected
        handleNodes: "node", // selector/filter function for whether edges can be made from a given node
        snap: false, // when enabled, the edge can be drawn by just moving close to a target node (can be confusing on compound graphs)
        snapThreshold: 50, // the target node must be less than or equal to this many pixels away from the cursor/finger
        snapFrequency: 15, // the number of times per second (Hz) that snap checks done (lower is less expensive)
        noEdgeEventsInDraw: false, // set events:no to edges during draws, prevents mouseouts on compounds
        disableBrowserGestures: true, // during an edge drawing gesture, disable browser gestures such as two-finger trackpad swipe and pinch-to-zoom

        ghostEdgeParams: function () {
            // return element object to be passed to cy.add() for the ghost edge
            // (default classes are always added for you)
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
                content: '<span class="fa fa-copy fa-2x" ></span>',
                select: function () {
                    supp.move();
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
                "name": type,
                "id": nom
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
            cy.remove("node:selected");
            cy.remove("edge:selected");
            createArray(cy);
        }

        if (e.keyCode === 27) {
            jQuery('#collapseExample').collapse('hide');
            createArray(cy);
        }

    }, false);

    //Event lors de la fin de la création d"un edge
    cy.on("ehcomplete", (event, sourceNode, targetNode) => {
        createArray(cy);
    });


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
                    "data": {},
                    "data_ready": {},
                    "on_launch": false
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