var STUDENT_METHOD ={

        handlerData:function(resJSON){

            var templateSource   = $("#student-template").html(),

                template = Handlebars.compile(templateSource),

                studentHTML = template(resJSON);

           $('#my-container').html(studentHTML);
            
        },
        loadStudentData : function(){
            $.ajax({
                url:"http://planetera.localhost/studentData.json",
                method:'get',
                success:this.handlerData

            })
        }
};

$(document).ready(function(){
 //   alert("this is a test!");

    var planetDescriptions = [
	{ name: "Test 1", subdir:"wfs", description:"<p>Thi sis a description paragraph.</p>" },
	{ name: "Test 2", subdir:"wfs", description:"<p>Lorem ipsum rh rah rah</p>" },
	{ name: "Test 3", subdir:"wfs", description:"<p>To get the feeling of how it works, here is the same demo again, but this time I have used a special Sample Viewer script which is integrated into my blog, so that if you mouse over the demo, you will see a little '+' button that you can click on. The result will be a tabbed view in which you can see the data and the template, as well as the result: </p>" },
    ];
         
    $(".planetDescriptionContainer").loadTemplate($("#planetDescriptionTemplate"), planetDescriptions);


});
