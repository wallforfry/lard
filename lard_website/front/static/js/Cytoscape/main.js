document.addEventListener("DOMContentLoaded", function () {
    var data = {
        "nodes": [
            {
                "data": {
                    "id": "BLUR",
                    "name": "Blur"
                }
            },
            {
                "data": {
                    "id": "IMAGE",
                    "name": "Image"
                }
            }
        ],
        "edges": [
            {
                "data": {
                    "target": "BLUR",
                    "source": "IMAGE"
                }
            }
        ]
    }

    //initCytoscape(data);
});

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

    cy.cxtmenu({
        selector: 'node, edge',

        commands: [
            {
                content: 'TEST',
                select: function (ele) {
                    cy.remove(ele);
                }
            },

            {
                content: '<span class="fa fa-star fa-2x" ></span>',
                select: function (ele) {
                    console.log(ele.data('name'));
                },
                enabled: false
            },

            {
                content: '<span class="fa fa-remove fa-2x" style="color: #c53a3a;"></span>',
                select: function (ele) {
                    cy.remove(ele);
                },
                activeFillColor: 'rgba(255,0,0,0.2)',
            }
        ]
    });

    cy.cxtmenu({
        selector: 'core',

        commands: [
            {
                content: 'bg1',
                select: function () {
                    console.log('bg1');
                }
            },

            {
                content: 'bg2',
                select: function () {
                    console.log('bg2');
                }
            }
        ]
    });

    var num = 1;

    //Permet de delete nodes et edges avec bouton "Remove"
    document.querySelector("#clear").addEventListener("click", function () {
        cy.remove("node:selected");
        cy.remove("edge:selected");
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
                "id" : type,
            },
            position: {
                x: Math.floor(Math.random() * (cy.width() - 500)) + 300,
                y: Math.floor(Math.random() * (cy.height() - 500)) + 100
            }
        });


        cy.pan();
        cy.center();
        num++;
        console.log(cy.width());
    });


    //Permet de delete nodes et edges avec "Suppr"
    document.addEventListener("keydown", function (e) {
        if (e.keyCode === 46) {
            cy.remove("node:selected");
            cy.remove("edge:selected");
        }
    }, false);

    //Event lors de la fin de la création d"un edge
    cy.on("ehcomplete", (event, sourceNode, targetNode) => {
        console.log(cy.elements().jsons());
    });

}