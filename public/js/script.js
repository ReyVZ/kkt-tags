res = [];
output = "";
scan_form = function () {
    el = document.forms.doc.elements
    types = "[";
    for (e in el) {
        if (el[e].checked == true) {
            types += el[e].name.slice(3) + ", ";
        }
    }
    types = types.length > 1 ? types.slice(0, types.length - 2) + "]" : "[]";
    return types

}
add_tag = function (id) {
    btn = document.getElementById("button" + id);
    if (btn.innerHTML == "Добавить") {
        fn = document.getElementById("select" + id);
        el = document.getElementById("tag" + id);
        el.classList.add("added");
        btn.innerHTML = "Удалить";
        if (fn != null && fn.value != "---") {
            res.push(fn.value + "(" + id + ")");
        } else {
            res.push(id);
        }
        if (fn != null) {
            fn.setAttribute("disabled", "");
        }
        reset();
    }
    else {
        fn = document.getElementById("select" + id);
        el = document.getElementById("tag" + id);
        el.classList.remove("added");
        btn.innerHTML = "Добавить";
        if (fn != null && fn.value != "---") {
            res.splice(res.indexOf(fn.value + "(" + id + ")"), 1);
        } else {
            res.splice(res.indexOf(id), 1);
        }
        if (fn != null) {
            fn.removeAttribute("disabled");
        }
        reset();
    }
}
reset = function () {
    output = "{\n\t\"filter\":{\n\t\t\"forDocumentTypes\": " + scan_form() + "\n\t},\n\t\"output\": {\n\t\t\"fields\": [\n";
    for (r in res) {
        if (isNaN(res[r])) {
            s = res[r];
            id = parseInt(s.slice(s.indexOf("(") + 1, s.indexOf(")")));
            fn = s.slice(0, s.indexOf("("));
            d = data.filter(function (x) { return x["id"] == id })[0];
            output += "\t\t\t{ \"key\": \"" + d.key + "\", \"DisplayName\": \"" + d.default +
                "\", \"function\": \"" + fn + "\" },\n";
        } else {
            d = data.filter(function (x) { return x["id"] == res[r] })[0];
            output += "\t\t\t{ \"key\": \"" + d.key + "\", \"DisplayName\": \"" + d.default + "\" },\n";
        }
    }
    output = output.slice(0, output.length - 2) + "\n\t\t]\n\t}\n}";
    document.getElementById("output").innerHTML = output;
}
xhr = new XMLHttpRequest();
xhr.open('GET', '/generator', false);
xhr.send();
data = JSON.parse(xhr.responseText);
table = "";
for (d in data) {
    table += "<tr id=\"tag" + data[d].id + "\">\
            <td>" + data[d].id + "</td>\
            <td>" + data[d].key + "</td>\
            <td>" + data[d].description + "</td>\
            <td>" + data[d].default + "</td>\
            <td>" + data[d].doc + "</td>\
            <td>" + (data[d].aggr == true ?
            "<select id=\"select" + data[d].id + "\">\
                    <option value=\"---\">---</option>\
                    <option value=\"sum\">sum</option>\
                    <option value=\"count\">count</option>\
                    <option value=\"avg\">avg</option>\
                </select>": "") + "</td>\
            <td><button id=\"button" + data[d].id + "\" onclick=\"add_tag(" + data[d].id + ")\">Добавить</button></td>\
            </tr>"
}
tags = document.getElementById("tags");
tags.innerHTML = table;
doc_types = [1, 11, 2, 3, 31, 301, 4, 41, 401, 5];
form = "";
for (t in doc_types) {
    i = doc_types[t];
    form += "<label for=\"doc" + i + "\">" + i + "</label>" +
        "<input type=\"checkbox\" name=\"doc" + i + "\" id=\"doc" + i + "\">&nbsp&nbsp"
}
doc = document.forms.doc;
doc.innerHTML = form;
