const XLSX = require('xlsx');
const testBid = [{
    "title":'1',
    "body" : {
        "bidType":'2',
        "client":'3',
        "contractLength":'4',
        "location":'5',
        "postedDate":'6',
        "closingDate":'7',
        "estimatedStartDate":'8'
    },
    "url":'9'
}]

function sortFunction(a, b) {
  if (a[0] === b[0]) {
      return 0;
  }
  else {
      return (a[0] < b[0]) ? -1 : 1;
  }
}

function displayApps() {
    //Load JSON from local storage into app
    var keys = Object.entries(localStorage).filter(element => { return element[0].indexOf("dos_app_") != -1 });
    var table = document.getElementById("app_list");
    table.innerHTML = "<tr><th style = \"width: 80%;\"> Title</th><th style=\"width: 20%;\">Delete</th></tr >";

    keys = (keys.sort(sortFunction));
    for (key in keys) {
        var row = document.createElement("tr");
        var title = document.createElement("td");
        let del = document.createElement("td");

        title.id = keys[key][0];

        if (JSON.parse(keys[key][1]).title.length > 20) {
            title.innerHTML = JSON.parse(keys[key][1]).title.substring(0, 20) + "...";
        } else {
            title.innerHTML = JSON.parse(keys[key][1]).title;
        }

        del.appendChild(document.createElement("i"));
        del.children[0].className = "fa fa-remove";
        del.children[0].style.color = "red";

        let counter = keys[key][0]; // IMPORTANT CODE to sync variable event listener otherwise all buttons have same ID due to bug
        del.children[0].addEventListener('click', function(counter) {
            localStorage.removeItem(counter);
            displayApps();
        }.bind(null, counter));

        row.appendChild(title);
        row.appendChild(del);
        table.appendChild(row);
    }
}

window.onload = function () {
    displayApps();
}

document.getElementById("add").addEventListener('click', () => {
    function modifyDOM() {
        var client = document.evaluate("/html[@class='govuk-template ']/body[@class='govuk-template__body  js-enabled']/div[@class='govuk-width-container ']/main[@id='main-content']/div[@class='govuk-grid-row'][1]/div[@class='govuk-grid-column-two-thirds']/span[@class='govuk-caption-l']/child::text()", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
        var contractLength = document.evaluate("//dt[contains(text(), 'Expected contract length')]//..//dd/child::text()", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
        var location = document.evaluate("//dt[contains(text(), 'Location')]//..//dd/child::text()", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
        var postedDate = document.evaluate("//dt[contains(text(), 'Published')]//..//dd/child::text()", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
        var closingDate = document.evaluate("//dt[contains(text(), 'Closing date for applications')]//..//dd/child::text()", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
        var estimatedStartDate = document.evaluate("//dt[contains(text(), 'Expected contract length')]//..//dd/child::text()", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
        var value = document.evaluate("//dt[contains(text(), 'Budget range')]//..//dd/child::text()", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;

        if (value == null) {
            var value = document.evaluate("//dt[contains(text(), 'Maximum day rate')]//..//dd/child::text()", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
        }

        var returnJson = {"bidType" : "DOS Stage 1",
                          "client" : client.nodeValue.replace('\n','').trim(),
                          "contractLength" : contractLength.nodeValue.replace('\n','').trim(), //Standardise data
                          "location" : location.nodeValue.replace('\n','').trim(),
                          "postedDate" : postedDate.nodeValue.replace('\n','').trim(),
                          "closingDate" : closingDate.nodeValue.replace('\n','').trim(),
                          "estimatedStartDate" : estimatedStartDate.nodeValue.replace('\n','').trim(),
                          "value" : value.nodeValue.replace('\n','').trim()
                          }
        return returnJson;
    }

    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) { //We have permission to access the activeTab, so we can call chrome.tabs.executeScript:

      var tabId = tabs[0].id; //Required for script execution in context of tab
      var url = tabs[0].url; //URL for JSON
      var title =  tabs[0].title; //title for JSON

      if (url.split(".gov.uk")[0] != "https://www.digitalmarketplace.service"){
        alert("Please ensure you are on a https://www.digitalmarketplace.service.gov.uk/ page")
      } else {
        chrome.scripting.executeScript({
          target: {tabId: tabId},
          func: modifyDOM, //argument here is a string but function.toString() returns function's code
        }, (results) => {
        var body = results[0].result; //Here we have just the innerHTML and not DOM structure

        if (Object.entries(localStorage).length == 0) {
            //Create local storage for apps and id counter (we are not recycling id's!!)
            localStorage.setItem("dos_app_1", JSON.stringify({
                "title": title,
                "body":  body ,
                "url": url
            }));
            localStorage.setItem("dos_key", "2");
        } else {
            //Add new record and increment id
            localStorage.setItem("dos_app_" + localStorage.getItem("dos_key"), JSON.stringify({
                "title": title,
                "body":  body,
                "url": url
            }));

            var inc_id = parseInt(localStorage.getItem("dos_key")) + 1;
            console.log("this one", inc_id);
            localStorage.setItem("dos_key", inc_id.toString())
        }
        displayApps();
      });
      }
    });
});

document.getElementById("restart").addEventListener('click', () => {
    localStorage.clear();
    displayApps();
});

document.getElementById("export").addEventListener('click', () => {
    // Get opportunities from JSON
    const opportunityArray = [];
    for(let i = 0; i < Object.entries(localStorage).length; i++){
        const keyName = localStorage.key(i);
        if(keyName.startsWith("dos_app")){
            console.log(localStorage.getItem(keyName))
            opportunityArray.push(JSON.parse(localStorage.getItem(keyName)))
        }
    }

    // Create Excel file blob
    const fileBlob = createExcelBlob(opportunityArray)

    // Download Excel file
    downloadFile(fileBlob);
})

function downloadFile(fileBlob) {
    const url = URL.createObjectURL(fileBlob)
    chrome.downloads.download({
        url: url,
        filename: "opportunities_export.xlsx"
    })
}

function createExcelBlob(bidList) {
    var wb = XLSX.utils.book_new();
    wb.Props = {
        Title: "Bid List",
        Subject: "Bids",
        Author: " ",
        CreatedDate: Date.now()
    };
    wb.SheetNames.push("Test Sheet");
    var excelData = addBidsToArray(bidList);
    var ws = XLSX.utils.aoa_to_sheet(excelData);
    wb.Sheets["Test Sheet"] = ws;
    var wbout = XLSX.write(wb, {bookType:'xlsx',  type: 'binary'});
    return new Blob([s2ab(wbout)],{type:"application/octet-stream"});
}

function s2ab(s) { 
    var buf = new ArrayBuffer(s.length); //convert s to arrayBuffer
    var view = new Uint8Array(buf);  //create uint8array as viewer
    for (var i=0; i<s.length; i++) view[i] = s.charCodeAt(i) & 0xFF; //convert to octet
    return buf;    
}

function addBidsToArray(bidList) {
    var data = [
        [
            'Bid Type',
            'Client',
            'Title',
            'Value £',
            'Contract Length',
            'Location',
            'Posted Date',
            'Closing Date',
            'Estimated Start Date',
            'Link',
            'Decision',
            'Team',
            'Priority'
        ]
    ]
    for (let i = 0; i < bidList.length; i++) {
        var row = [
            bidList[i]['body']['bidType'],
            bidList[i]['body']['client'],
            bidList[i]['title'],
            bidList[i]['body']['value'],
            bidList[i]['body']['contractLength'],
            bidList[i]['body']['location'],
            bidList[i]['body']['postedDate'],
            bidList[i]['body']['closingDate'],
            bidList[i]['body']['estimatedStartDate'],
            bidList[i]['url'],
            '',
            '',
            ''
        ]
        data.push(row)
    }
    return data
}