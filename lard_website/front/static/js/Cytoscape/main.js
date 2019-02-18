document.addEventListener('DOMContentLoaded', function () {
    var cy = window.cy = cytoscape({

        container: document.getElementById('cy'),

        layout: {
            name: 'grid',
            rows: 2,
            cols: 2
        },

        style: [
            {
                selector: 'node',
                style: {
                    'content': 'data(name)',
                    'shape': 'square',
                }
            },

            {
                selector: 'edge',
                style: {
                    'curve-style': 'bezier',
                    'content': 'data(name)',
                    'target-arrow-shape': 'triangle'
                }
            },

            // some style for the extension

            {
                selector: '.eh-handle',
                style: {
                    'background-color': 'red',
                    'width': 12,
                    'height': 12,
                    'shape': 'ellipse',
                    'overlay-opacity': 0,
                    'border-width': 12, // makes the handle easier to hit
                    'border-opacity': 0
                }
            },

            {
                selector: '.eh-hover',
                style: {
                    'background-color': 'red'
                }
            },

            {
                selector: '.eh-source',
                style: {
                    'border-width': 2,
                    'border-color': 'red'
                }
            },

            {
                selector: '.eh-target',
                style: {
                    'border-width': 2,
                    'border-color': 'red'
                }
            },

            {
                selector: '.eh-preview, .eh-ghost-edge',
                style: {
                    'background-color': 'red',
                    'line-color': 'red',
                    'target-arrow-color': 'red',
                    'source-arrow-color': 'red'
                }
            },

            {
                selector: '.eh-ghost-edge.eh-preview-active',
                style: {
                    'opacity': 0
                }
            }
        ],

        elements: {
            nodes: [
                {data: {id: 'j', name: 'Alex'}},
                {data: {id: 'e', name: 'Jojo'}},
                {data: {id: 'k', name: 'Walle'}},
                {data: {id: 'g', name: 'Pilou'}}
            ],
            edges: [
                {data: {source: 'j', target: 'e'}},
                {data: {source: 'j', target: 'k'}},
                {data: {source: 'j', target: 'g'}},
                {data: {source: 'e', target: 'j'}},
                {data: {source: 'e', target: 'k'}},
                {data: {source: 'k', target: 'j'}},
                {data: {source: 'k', target: 'e'}},
                {data: {source: 'k', target: 'g'}},
                {data: {source: 'g', target: 'j'}}
            ]
        }
    });

    let defaults = {
        preview: true, // whether to show added edges preview before releasing selection
        hoverDelay: 150, // time spent hovering over a target node before it is considered selected
        handleNodes: 'node', // selector/filter function for whether edges can be made from a given node
        snap: false, // when enabled, the edge can be drawn by just moving close to a target node (can be confusing on compound graphs)
        snapThreshold: 50, // the target node must be less than or equal to this many pixels away from the cursor/finger
        snapFrequency: 15, // the number of times per second (Hz) that snap checks done (lower is less expensive)
        noEdgeEventsInDraw: false, // set events:no to edges during draws, prevents mouseouts on compounds
        disableBrowserGestures: true, // during an edge drawing gesture, disable browser gestures such as two-finger trackpad swipe and pinch-to-zoom
        handlePosition: function (node) {
            return 'middle top'; // sets the position of the handle in the format of "X-AXIS Y-AXIS" such as "left top", "middle top"
        },
        handleInDrawMode: false, // whether to show the handle in draw mode
        edgeType: function (sourceNode, targetNode) {
            // can return 'flat' for flat edges between nodes or 'node' for intermediate node between them
            // returning null/undefined means an edge can't be added between the two nodes
            return 'flat';
        },
        loopAllowed: function (node) {
            // for the specified node, return whether edges from itself to itself are allowed
            return false;
        },
        nodeLoopOffset: -50, // offset for edgeType: 'node' loops
        nodeParams: function (sourceNode, targetNode) {
            // for edges between the specified source and target
            // return element object to be passed to cy.add() for intermediary node
            return {};
        },
        edgeParams: function (sourceNode, targetNode, i) {
            // for edges between the specified source and target
            // return element object to be passed to cy.add() for edge
            // NB: i indicates edge index in case of edgeType: 'node'
            return {};
        },
        ghostEdgeParams: function () {
            // return element object to be passed to cy.add() for the ghost edge
            // (default classes are always added for you)
            return {};
        },
        show: function (sourceNode) {
            // fired when handle is shown
        },
        hide: function (sourceNode) {
            // fired when the handle is hidden
        },
        start: function (sourceNode) {
            // fired when edgehandles interaction starts (drag on handle)
        },
        complete: function (sourceNode, targetNode, addedEles) {
            // fired when edgehandles is done and elements are added
        },
        stop: function (sourceNode) {
            // fired when edgehandles interaction is stopped (either complete with added edges or incomplete)
        },
        cancel: function (sourceNode, cancelledTargets) {
            // fired when edgehandles are cancelled (incomplete gesture)
        },
        hoverover: function (sourceNode, targetNode) {
            // fired when a target is hovered
        },
        hoverout: function (sourceNode, targetNode) {
            // fired when a target isn't hovered anymore
        },
        previewon: function (sourceNode, targetNode, previewEles) {
            // fired when preview is shown
        },
        previewoff: function (sourceNode, targetNode, previewEles) {
            // fired when preview is hidden
        },
        drawon: function () {
            // fired when draw mode enabled
        },
        drawoff: function () {
            // fired when draw mode disabled
        }
    };

    var eh = cy.edgehandles(defaults);

    //Permet de delete nodes et edges avec bouton "Remove"
    document.querySelector('#clear').addEventListener('click', function () {
        cy.remove('node:selected');
        cy.remove('edge:selected');
    });

    //Permet de delete nodes et edges avec "Suppr"
    document.addEventListener('keydown', function (e) {
        if (e.keyCode === 46) {
            cy.remove('node:selected');
            cy.remove('edge:selected');
        }
    }, false);

    //Event lors du début de la création d'un edge
    cy.on('ehstart', (event, sourceNode, targetNode, addedEles) => {
        console.log("Edge : " + sourceNode.id() + " à " + targetNode.id());

    });

    //Event lors de la fin de la création d'un edge
    cy.on('ehcomplete', (event, sourceNode, targetNode, addedEles) => {
        console.log("Edge : " + sourceNode.id() + " à " + targetNode.id());

    });

});

