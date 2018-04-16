function remove_recipe_row(button) {
    var row = button.parentNode.parentNode;
    row.parentElement.removeChild(row);

    removed_elemtents++;

    decrement_ingredient_count();
}

function add_row() {
    var total_tries = removed_elemtents + parseInt(document.getElementById('total_ingredients').value, 10); 

    for(var i = 0; i < total_tries; i++) {
        var name = 'ingredient' + i;
        var element = document.getElementById(name);

        if(element != undefined) {
            clone = element.cloneNode(true);
            var cloneId = total_tries;

            var select = get_child_by_id(clone, 'beverages' + i);
            select.id = 'beverages' + cloneId;
            select.name = 'beverage' + cloneId;

            var amount = get_child_by_id(clone, 'amount' + i);
            amount.id = 'amount' + cloneId;
            amount.name = 'amount' + cloneId;

            var button = get_child_by_id(clone, 'remove_button' + i)
            button.id = 'remove_button' + cloneId;

            document.getElementById('form_recipe').insertBefore(clone, document.getElementById('submit-row'));

            increment_ingredient_count();

            break;
        }
    }
}

function increment_ingredient_count() {
    var element = document.getElementById('total_ingredients');
    var value = parseInt(element.value, 10);
    value = isNaN(value) ? 0 : value;
    value++;
    element.value = value;
}

function decrement_ingredient_count() {
    var element = document.getElementById('total_ingredients');
    var value = parseInt(element.value, 10);
    value = isNaN(value) ? 0 : value;
    value--;
    element.value = value;
}

function get_child_by_id(element, id) {
    
    for(var i = 0; i < element.childNodes.length; i++) {
        child = element.childNodes.item(i);
        if(strcmp(id, child.id) == 0) {
            return child;
        }
    }

    for(var i = 0; i < element.childNodes.length; i++) {
        child = element.childNodes.item(i);
        var possibleElement = get_child_by_id(child, id);
        if(possibleElement != undefined)
        return possibleElement;
    }
    
    return undefined;
}

function strcmp(a, b) {
    if(a == undefined && b == undefined)
        return 0;
    if(a == undefined)
        return 1;
    if(b == undefined)
        return -1;

    a = a.toString(), b = b.toString();
    for (var i=0,n=Math.max(a.length, b.length); i<n && a.charAt(i) === b.charAt(i); ++i);
    if (i === n) return 0;
    return a.charAt(i) > b.charAt(i) ? -1 : 1;
}


var removed_elemtents = 0;



