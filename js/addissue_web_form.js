//JavaScript used in addissue_web_form.php
function get_search_link()
{
	var site=document.getElementById('torrentsite');
	var file=document.getElementById('file');
	var searchstring=document.getElementById('searchstring');
	//alert(site.value);
	var request = new XMLHttpRequest();
	request.open("Get","js/searchlink.php?site="+site.value+"&search="+searchstring.innerHTML,false); 
	request.onreadystatechange = function () 
	{ 
		if (request.readyState == 4 && request.status == 200) 
		{ 
 			document.getElementById("searchlink").innerHTML = "Search "+site.value+" for "+searchstring.innerHTML;
			document.getElementById("searchlink").setAttribute('href',request.responseText);
		} 
	}
	request.send(null); 
}
function validate_issue_code()
{
	var issuecode=document.getElementById('issuecode');

	var request = new XMLHttpRequest();
	request.open("Get","js/validate_issue_code.php?issuecode="+issuecode.value,false); 
	request.onreadystatechange = function () 
	{ 
		if (request.readyState == 4 && request.status == 200) 
		{ 
 			document.getElementById("validcode").innerHTML = request.responseText
			document.getElementById("induckslink").setAttribute('href',"http://coa.inducks.org/issue.php?c="+issuecode.value);
			document.getElementById("induckslink").innerHTML = "Show "+issuecode.value+" on inducks";	
		} 
	}
	request.send(null); 
}
