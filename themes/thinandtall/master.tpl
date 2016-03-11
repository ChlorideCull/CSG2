<!DOCTYPE html>
<html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>{{title or 'No title set, fix!'}}</title>
        <link rel="stylesheet" href="/theme/sass/master.scss">
        <link rel="stylesheet" href="/theme/static/bebas_neue/BebasNeue.css">
        % for lnk in link_elements:
        <link rel="{{lnk[0]}}" href="{{lnk[1]}}">
        % end
    </head>
    <body>
        <header>
            <h1 class="title">{{title or 'No title set, fix!'}}</h1>
            <nav>
                % for pge in nav_links:
                <h1><a href="{{pge[0]}}">{{pge[1]}}</a></h1>
                % end
            </nav>
            <div class="clear"></div>
        </header>
        <div id="pagecontent">
        % include(content)
        </div>
    </body>
</html>