<h1>Annotate Image</h1>

<!--Form for collecting image URL -->

<hr color="grey">

<section class="editorContainer">
<!--Controls for CSS filters via range input-->
<div class="sliders">
  <div id="imageEditor">

  </div>
</div>

<!--container where image will be loaded-->
<!--<div id="imageContainer" class="center">
  <img src="https://s3-us-west-2.amazonaws.com/s.cdpn.io/123941/stadium.jpg">
</div>-->

<div id='imageContainer'>
    <img src ="data:image/png;base64, {image}" alt="" id="image">
    <button id="{previous}" class="button">  Previous </button>
    <button id="{next}" class="button">  Next </button>
    <button id="{skip}" class="button">  Skip </button>
    <button id="clear" class="button">  Reset </button>
    <div id="rect"></div>
</div>
 </section>


<style>
    /* General styles for the page */
    .button {{
  background-color: gray; /* Green */
  border: none;
  color: white;
  padding: 15px 32px;
  text-align: center;
  text-decoration: none;
  display: inline-block;
  font-size: 16px;
  margin: 4px 2px;
  cursor: pointer;
  margin-top: 5px;
}}

.button:hover{{
  background:#E84F4F;
}}

* {{
  margin: 0;
  padding: 0;
  box-sizing:border-box;
}}

body {{
  font-family: monospace;
  max-width:940px;
  height:100vh;
  background: #111;
  color:#fff;
}}

h1 {{
  margin: 25px 0 25px 0;
  font-size: 40px;
  text-align: center;
  color:#fff;
}}

hr {{
  margin: 20px 0;
}}

form {{
  text-align: center;
}}

/* Styles for  URL box */

.url-box {{
  background-color: transparent;
  display: inline-block;
  height: 2em;
  border: none;
  border-bottom: 2px solid #fff;
  padding: 0px 0px 0px 20px;
  margin: 0px 0px;
  width: 50%%;
  outline: none;
  text-align: center;
  font-size: 15px;
  font-family: monospace;
  font-weight: 100;
  color: #fff;
}}

#go {{
  display: inline-block;
  height: 50px;
  width: 50px;
  background-color: transparent;
  padding: 0px;
  border: 2px solid #fff;
  border-radius: 50%%;
  box-shadow: none;
  cursor: pointer;
  outline: none;
  text-align: center;
  font-size: 20px;
  font-family: monospace;
  font-weight: 100;
  color: #fff;
}}

#go:hover{{
  background: #4B77BE;
}}

/* editor container */

.editorContainer{{
  display:grid;
  grid-gap: 10px;
  margin-top: 1.5rem;
  width: 95%%;
  margin: auto;
}}

/* Styles for image container*/

#imageContainer {{
  border-radius: 2px;
  padding: 0.15rem;
  max-width: 640px;
  border: 2px solid #111;
}}

#imageContainer img {{
  display:block;
  max-width: 100%%;
}}

/* Styles for sliders*/

.sliders {{
  border: 2px solid #fff;
  border-radius: 10px;
  padding-left: 10px;
  order: 1;
}}

.sliders p {{
  margin: 18px 0;
  vertical-align: middle;
}}

.sliders label {{
  display: inline-block;
  margin: 10px 0 0 0;
  width: 150px;
  font-size: 16px;
  color: #fff;
  text-align: left;
  vertical-align: middle;
}}

.sliders input {{
  position: relative;
  margin: 10px 20px 0 10px;
  vertical-align: middle;
}}

input[type=range] {{
  /*removes default webkit styles*/
  -webkit-appearance: none;
  /*fix for FF unable to apply focus style bug */
  border-radius: 5px;
  /*required for proper track sizing in FF*/
  width: 150px;
}}

input[type=range]::-webkit-slider-runnable-track {{
  width: 300px;
  height: 7px;
  background: #ABB7B7;
  border: none;
  border-radius: 3px;
}}

input[type=range]::-webkit-slider-thumb {{
  -webkit-appearance: none;
  border: none;
  height: 20px;
  width: 20px;
  border-radius: 50%%;
  background: #4B77BE;
  margin-top: -6px;
  vertical-align: middle;
}}
input[type=range]:focus {{
  outline: none;
}}

input[type=range]:hover {{
    cursor: pointer;
}}


.reset{{
  display: inline-block;
  height: 40px;
  width: 100px;
  background-color: transparent;
  padding: 0px;
  border: 2px solid #b3b3b1;
  border-radius: 10px;
  box-shadow: none;
  cursor: pointer;
  outline: none;
  text-align: center;
  font-size: 20px;
  font-family: monospace;
  font-weight: 100;
  color: #fff;
  margin: 0 0 10px 0;
  transition: 1s cubic-bezier(0, 1.27, 0.52, 1.5);

}}

.reset:hover{{
  background:#E84F4F;
}}

.p {{
  clear: both;
  text-align: center;
  padding:  20px 0 20px;
}}

/* Media queries */

@media (min-width:480px){{
  .editorContainer{{
    grid-template-columns: 1fr 2fr;
    align-items: left;
    width: 100%%;
  }}
  #imageContainer{{
    order:2;
  }}
}}
        .rect {{
            border: solid 2px red;
            pointer-events: none;
            display: none;
        }}

        </style>
<script type="text/javascript">
(function () {{
    var image = document.getElementById('image');
    var clear_button = document.getElementById('clear');
    var prev_button = document.getElementById('{previous}');
    var next_button = document.getElementById('{next}');
    var skip_button = document.getElementById('{skip}');

    var divs = {{
        rects_div: document.getElementById('rect'),
        bounds_div: document.getElementById('imageEditor')
    }};

    var box = initBox();
    image.setAttribute('draggable', false);
    image.addEventListener('mousedown', mousedown);
    image.addEventListener('mouseup', mouseup);
    image.addEventListener('mousemove', mousemove);
    clear_button.addEventListener('click', clearAll);
    prev_button.addEventListener('click', previous);
    next_button.addEventListener('click', next);
    skip_button.addEventListener('click', skip);

    var grab = false;
    var rect_count = 0;
    var buffer = {{
        xmins: [],
        xmaxs: [],
        ymins:[],
        ymaxs:[],

    }};

    var rects = [];

    var rect = {{
    x0: 0,
    y0: 0,
    x1: 0,
    y1: 0
    }};
    var client_rect = {{
    x0: 0,
    y0: 0,
    x1: 0,
    y1: 0
    }};

    function mousedown(e) {{
    grab = true;
    rect.x0 = e.offsetX;
    rect.y0 = e.offsetY;
    client_rect.x0 = e.clientX;
    client_rect.y0 = e.clientY;
    }}

    function mousemove(e) {{
    if (grab) {{
        rect.x1 = e.offsetX;
        rect.y1 = e.offsetY;
        client_rect.x1 = e.clientX;
        client_rect.y1 = e.clientY;
        showRect();
        }}
    }}

    function mouseup(e) {{
        grab = false;
        rects.push(rect)
        register(rect);
        rect_count++;
        box = initBox();
    }}

    function showRect() {{
        box.rect.style.display = 'block';
        box.rect.style.position = 'absolute';
        box.rect.style.left = client_rect.x0 + 'px';
        box.rect.style.top = client_rect.y0 + 'px';
        box.rect.style.width = (client_rect.x1 - client_rect.x0) + 'px';
        box.rect.style.height = (client_rect.y1 - client_rect.y0) + 'px';
        box.bounds.innerText = 'x: ' + rect.x0 + ', ' + rect.x1 + '\ny: ' + rect.y0 + ', ' + rect.y1;
    }}

    function register(rec){{
        buffer.xmins.push(rec.x0);
        buffer.xmaxs.push(rec.x1);
        buffer.ymins.push(rec.y0);
        buffer.ymaxs.push(rec.y1);
    }}

     function initBox(){{
    curr_box = {{
        rect: document.createElement("div"),
        bounds: document.createElement("label")
    }};

    divs.rects_div.appendChild(curr_box.rect);
    curr_box.rect.classList.add("rect");

    divs.bounds_div.appendChild(curr_box.bounds);
    return curr_box;
    }}

    function clearAll(){{
        rects = [];
        rect_count = 0;
        divs.rects_div.innerHTML = "";
        divs.bounds_div.innerHTML = "";
        box = initBox();
    }}

        function previous(){{
         google.colab.kernel.invokeFunction('{previous}');
    }}


        function next(){{
            var buffer = {{
                xmins : '[',
                xmaxs : '[',
                ymins : '[',
                ymaxs : '[',
            }};


            rects.forEach(function(item, index, array){{
                    buffer.xmins +=  item.x0 + ',';
                    buffer.xmaxs += item.x1 + ',';
                    buffer.ymins += item.y0 + ',';
                    buffer.ymaxs += item.y1 + ',';
                }});
            buffer.xmins += ']';
            buffer.xmaxs += ']';
            buffer.ymins += ']';
            buffer.ymaxs += ']';

      google.colab.kernel.invokeFunction('{next}',0,buffer);
    }}

        function skip(){{
      google.colab.kernel.invokeFunction('{skip}');
    }}

    }})();




</script>