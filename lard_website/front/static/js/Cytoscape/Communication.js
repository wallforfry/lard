let json = {
    "nodes":[],
    "edges":[]
};




function log(data) {
    console.log(data);
}
function addBlock(id, type) {
    json.nodes.push({
        "data" : {
            "id": id,
            "name":type
        }
    });
}

function addLiaison(source, target) {
    json.edges.push({
        "data" : {
            "target": target,
            "source": source
        }
    });
}

function getGraphJson() {
    return json;
}

/**
 *
 * @param {function} callbackFunction
 * Set the current graph json to the value return by api python
 * And pass it to the callback function in parameter
 */
function getGraphJsonFromPythonApi(callbackFunction, url){
    $.getJSON(url, function(data) {
    json = data;
    callbackFunction(data);
    });
}

// savePipeLine("{% url 'pipeline_edit' name=name %}");
// var url_cytosacape = "{% url 'pipeline_get_cytoscape' name=name %}";

function savePipeLine(url){
    $.post(url, function() {
  alert( "Success" );
}).fail(function() {
    alert( "Fail to save pipeline" );
  });
}









