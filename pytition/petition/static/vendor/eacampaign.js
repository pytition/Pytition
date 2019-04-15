/*
 * Javascript helper functions for handling ea3 campaign/form behavior.
 * NOTE: These js functions require at least jquery 1.3.2
 * Last Updated: 04/12/2010
 *
 */

   var a, pageTimer, warnMessage;
   function startClock(warnMsg) { 
      pageTimer = 0;
      warnMessage = warnMsg;
      a = window.setInterval('tick()', 60000); 
   }

   function tick() { 
      pageTimer++; 
      if (pageTimer == 28) { 
         warnuser(); 
      }
   }
   
   function warnuser() { 
      if (confirm(warnMessage)) {
         var url = CONTEXT_ROOT + '/action.retrievefile.do?sess=true';
         $.post(url, function(data) {pageTimer = 0;});
      }
   }

   function validateEAform(form, ajax, callIcon, callColor) {
      // call validatefield to do all dynamic validations first
      var emptyparams = '';
      for(x = 0; x < form.elements.length; x++) {
         var ele = form.elements[x];
         if(ele.type != 'button' && ele.type != 'submit' && ele.type != 'reset') {
            if($(ele).attr("onBlur") != undefined) {
               if(ele.type != 'checkbox' && ele.type != 'radio') {
                  validatefield(ele, true, callIcon, callColor);
               } else {
                  var val = $('input[name=' + ele.name + ']:checked').val();
                  if(!val) {
                     validatefield(ele, true, callIcon, callColor);
                     if(emptyparams.indexOf(ele.name) == -1) {
                        emptyparams = emptyparams + '&' + escape(ele.name) + '=';
                     }
                  }
               }
            }
         }
      }

      // check entire form if anything is invalid
      var isValid = true;
      var params = $(form).serialize() + emptyparams;
      var url = CONTEXT_ROOT + '/form.validate.do'; // + params + emptyparams;
      var resp = $.ajax({type: 'post', url: url, data: params, async: false}).responseText;
      if(resp != '') {
         isValid = false;
         $('#eaerrors').html(resp);
         $('html, body').animate( {scrollTop: 0}, 'slow' );
         $('#errorheading').focus();
      }
      if (isValid && ! ajax) {
      	disableSubmitButton();
      }
      return isValid;
   }
	
   function disableSubmitButton() {
      $('.eaSubmitButton').attr('disabled', 'disabled');
      $('.eaSubmitButton').addClass('isDisabled');
      return true;
   }
   
   function gettextresponse(params, eleName) {
      var url = CONTEXT_ROOT + '/formfield.validate.do?' + params;
      $.post(url, function(data) {
         var divId = eleName;
         divId = divId.replace(/ /g, '_') + 'Error';
         if(data == '') {
            $('#' + divId).addClass('eaErrorMessageHide');
         $('#' + divId).html(data);
         } else {
            $('#' + divId).removeClass('eaErrorMessageHide');
            $('#' + divId).html(data);
         }
      });
   }

   function geticonresponse(params, eleName) {
      var url = CONTEXT_ROOT + '/formfield.icon.do?' + params;
      $.post(url, function(data) {
         var divId = eleName;
         divId = divId.replace(/ /g, '_') + 'Icon';
         $('#' + divId).html(data);
      });
   }

   function getcolorresponse(params, eleName) {
      var url = CONTEXT_ROOT + '/formfield.color.do?' + params;
      $.post(url, function(data) {
         var divId = eleName;
         divId = divId.replace(/ /g, '_') + 'Div';
         if(data == '') {
            $('#' + divId).removeClass('eaFieldErrorHighlightColor');
         } else {
            $('#' + divId).addClass('eaFieldErrorHighlightColor');
         }
      });
   }

   function validatefield(ele, callText, callIcon, callColor) {
      // ajax in the validation text
      var params = $(ele).serialize();
      params = params + '&name=' + escape(ele.name);
      params = params + '&ea.form.id=' + $('[name=ea\\.form\\.id]').val();
      params = params + '&ea.campaign.id=' + $('[name=ea\\.campaign\\.id]').val();

      // ajax in the text response
      if(callText) {
      gettextresponse(params, ele.name);
      }

      // ajax in the validation icon (if configured)
      if(callIcon) {
      geticonresponse(params, ele.name);
      }

      // ajax in the error highlight color (if configured)
      if(callColor) {
      getcolorresponse(params, ele.name);
      }

      return false;
   }

   function validatetriple(ele) {
      var name = ele.name.substring(0, ele.name.length-1);
      var params = 'name=' + escape(name);
      params = params + '&ea.form.id=' + $('[name=ea\\.form\\.id]').val();
      params = params + '&ea.campaign.id=' + $('[name=ea\\.campaign\\.id]').val();
      
      var id = name.replace(/ /g, '_');
      var val = escape($('#'+ id + '1').val());
      params += '&' + name + '=' + val;
      val = escape($('#'+ id + '2').val());
      params += '&' + name + '=' + val;
      val = escape($('#'+ id + '3').val());
      params += '&' + name + '=' + val;

      // ajax in the text response
      gettextresponse(params, name);

      // ajax in the validation icon (if configured)
      geticonresponse(params, name);

      // ajax in the error highlight color (if configured)
      getcolorresponse(params, name);

   }

   function validateSame(ele) {
      var name = escape(ele.name.replace(/Confirm/, ''));
      var id = ele.name.replace(/ /g, '_');
      id = id.replace(/Confirm/, '');
      var params = 'name=' + name;
      params = params + '&ea.form.id=' + $('[name=ea\\.form\\.id]').val();
      params = params + '&ea.campaign.id=' + $('[name=ea\\.campaign\\.id]').val();

      // pass both email addresses back for validation
      params = params + '&' + name + '=' + ele.value + '||' + $('#' + id).val();

      // ajax in the text response
      gettextresponse(params, ele.name);
      
      // ajax in the validation icon (if configured)
      geticonresponse(params, ele.name);

      // ajax in the error highlight color (if configured)
      getcolorresponse(params, ele.name);
      
      return false;
   }

   function checkdep(ele) {
      var frm = ele.form;
      var params = $(frm).serialize();
      params = params + '&ea.dependency.param=' + escape(ele.name);
      var url = CONTEXT_ROOT + '/formfield.dependency.do';
      $.ajax({
          type: 'post',
          url: url,
          dataType: 'json',
          data: params,
          async: false,
          cache: false,
          success: function(response) {
         	if(response) {
	            for(var x = 0; x < response.length; x++) {
	               var data = response[x];
	               for(var key in data) {
	                  if(key.indexOf("redirect") != -1) {
	                     var redirectUrl = data[key];
                        if(redirectUrl.indexOf(CONTEXT_ROOT) >= 0) {
                           var syncUrl = CONTEXT_ROOT + "/action?ea_sync_request=true";
                           var syncParams = getSyncParameters(frm);
                           if (syncParams.length > 0) {
                              syncUrl += '&' + syncParams;
                           }
                           $.ajax({
                              type: 'post',
                              url: syncUrl,
                              dataType: 'json',
                              async: false,
                              cache: false,
                              success: function(response2) {
                                 redirectUrl += '&' + getRedirectParameters(frm);
                              }
                           });
                        }
	                     window.location.href = redirectUrl;
	                  }
	                  else if(key == "display_textfield") {
	                     // disable current fields with this name
	                     var eles = document.getElementsByName(ele.name);
	                     if(eles) {
	                        for(x = 0; x < eles.length; x++) {
	                           eles[x].disabled = true;
	                        }
	                     }
	
	                     // add new field text field for this element
	                     var divId = ele.name;
	                     divId = divId.replace(/ /g, '_') + 'Div';
	                     $('#' + divId).append(data[key]);
	                  }
	                  else if(key == "hide") {
	                     changefield(key, data[key]);
	                  }
	                  else if(key == "display") {
	                     changefield(key, data[key]);
	                  }
	                  else if(key == "changeoptions") {
	                     changeoptions(data[key]);
	                  } 
	                  else if(key == "changeradios") {
	                     changeradios(data[key]);
	                  }
	                  else {  // calculation
	                     divId = key;
	                     divId = divId.replace(/ /g, '_');
	                     $('#' + divId).val(data[key]);
	                     $('#' + divId).attr("readonly", true);
	                  }
               	  }
              }
           }
           }
      });
      return false;
   }

   function getSyncParameters(form) {
      var params = 'ea.campaign.id=' + $("input[name=ea\\.campaign\\.id]").val()
      				+ '&ea.client.id=' + $("input[name=ea\\.client\\.id]").val()
      				+ '&sessionId=' + $("input[name=sessionId]").val();
      for(x = 0; x < form.elements.length; x++) {
         var ele = form.elements[x];
         if(ele.type != 'button' && ele.type != 'submit' && ele.type != 'reset') {
            if($(ele).attr("onBlur") != undefined) {
               if(ele.type != 'checkbox' && ele.type != 'radio') {
                  params = params + '&' + escape(ele.name) + '=' + escape(ele.value);
               } 
               else {
                  var val = $('input[name=' + ele.name + ']:checked').val();
                  if(val && params.indexOf(ele.name) == -1) {
                     params = params + '&' + escape(ele.name) + '=' + escape(val);
                  }
               }
            }
         }
      }

      return params;
   }

   function getRedirectParameters(form) {
      var params = 'ea_redirect=true&sessionId=' + $("input[name=sessionId]").val();
      return params;
   }

   function changeoptions(values) {
      var options = values.split('~');
      if(options.length > 1) {
         var field = options[0].replace(/ /g, '_');
         $('#' + field).children().remove().end();
         for(x = 1; x < options.length; x++) {
            var checked = '';
            var vals = options[x].split('||');
            if(vals[1].indexOf("[check]") > -1) {
               vals[0] = vals[0].replace(/\[check\]/, '');
               vals[1] = vals[1].replace(/\[check\]/, '');
               checked = 'selected';
            }
            $('#' + field).append('<option value="' + vals[1] + '" ' + checked + '>' + vals[0] + '</option>');
         }
         changefield('display', field);
      }
   }
   
   function changeradios(values) {
      var options = values.split('~');
      if(options.length > 2) {
         var name = options[0];
         var fieldId = options[0].replace(/ /g, '_');
         var type = options[1];
         var layout = options[2];
         var html = '<span class="eaFormRadio">';
         var vals = '';
         for(x = 3; x < options.length; x++) {
            vals = options[x].split('||');
            var checked = '';
            var func = type == 4 ? 'onblur="validatefield(this, true, true, true);" onclick="checkdep(this);"' : 'onchange="toggleOptionInput(this);"';
            if(vals[0].indexOf("[check]") > -1) {
               vals[0] = vals[0].replace(/\[check\]/, '');
               checked = 'checked ';
            }
            if(vals[1].indexOf("[check]") > -1) {
               vals[1] = vals[1].replace(/\[check\]/, '');
               checked = 'checked ';
            }
            
            html += '<input id="' + vals[1] + '" name="' + name + '" value="' + vals[1] + '" ' + checked + func + ' type="radio">';
            html += '<label for="' + vals[1] + '">' + vals[0] + '</label>';
            
            // for radio with input, we need to add the input field
            if(type == 9 && x == (options.length-1)) {
               var inputId = vals[1].replace(/ /g, '_') + 'Input';
               html += '&nbsp;&nbsp;&nbsp;'
               html += '<input id="' + inputId + '" class="eaRadioTextfield" type="text" disabled style="display:none" name="' + name + '">';
            } 
            html += layout == 1 ? '<br/>' : '';
         }
         
         html += '<span id="' + fieldId + 'Icon" class="eaValidationIcon">&nbsp;</span>';
         html += '</span>';
         $('#'+fieldId+'Field').html(html);

         changefield('display', fieldId);
      }
   }

   function changefield(action, field) {
      var fieldDiv;
      if(action == 'display') {
         fieldDiv = field.replace(/ /g, '_') + 'Div';
         $('#' + fieldDiv).show();
         $('#' + fieldDiv).find('input, textarea, button, select').removeAttr('disabled');
         $('#' + field + 'Input').hide();
         $('#' + field + 'Input').attr('disabled',true);
      }
      else if(action == 'hide') {
         fieldDiv = field.replace(/ /g, '_') + 'Div';
         $('#' + fieldDiv).hide();
         $('#' + field + 'Input').hide();
         $('#' + fieldDiv).find('input, textarea, button, select').attr('disabled',true);
      }
   }

   function removeother(id) {
      var eles = document.getElementsByName(id);
      var other = id.replace(/ /g, '_') + 'OtherSpan';
      if(eles && eles.length > 0) {
         $('#' + other).remove();
         for(x = 0; x < eles.length; x++) {
            eles[x].disabled = false;
            if(eles[x].type == 'radio') {
               eles[x].checked = false;
            } else {
               $(eles[x]).val(1);
            }
         }
      }
   }
   
   function doEAPageRefresh(theForm) {
      if(theForm) {
         theForm.reset();
         theForm.ea_requested_action.value = "campaign_page_refresh";
         theForm.submit();
      }
   }
   
   function doEAAjaxPageRefresh(theForm) {
      if(theForm) {
         theForm.ea_requested_action.value = "campaign_page_refresh";
         doAJAXForm(theForm, "eaAjaxContent", false);
      }
   }
   
   function hideFormButtons(pageNumber) {
      var divName = "eaFormClose_" + pageNumber;
      var theDiv = document.getElementById(divName);
      if (theDiv) {
         theDiv.style.display = "none";
      }
   }

   function toggleOptionInput(ele) {
      var val = $(ele).val();
      var inp = '';
      var lastOption = '';
      if(ele.type == 'select-one') {
         $(ele).find('option').each(function() {
            lastOption = $(this).val();
         });
         inp = '#' + ele.id + 'Input';
      } else if(ele.type == 'radio') {
         $("input:radio[name='" + ele.name + "']").each(function() {
            lastOption = $(this).val();
         });
         inp = '#' + lastOption.replace(/ /g, '_') + 'Input';
      }

      if(val == lastOption) {
         $(inp).removeAttr("disabled");
         $(inp).show();
      } else {
         $(inp).attr("disabled", true);
         $(inp).hide();
      }

      return false;
   }

   function showHideBiography(contactId) {
      var bioContainer = document.getElementById("eaContactBiographyContainer_" + contactId);
      if (bioContainer) {
         if (bioContainer.style.display == "none") {
            bioContainer.style.display = "";
         } else {
            bioContainer.style.display = "none";
         }
      }
   }
   
   function showHideContactDetail(contactId) {
      var theDetailDiv = document.getElementById("ea_contact_detail_" + contactId);
      if (theDetailDiv.style.display == "none") {
         theDetailDiv.style.display = "";
      } else {
         theDetailDiv.style.display = "none";
      }
   }
   