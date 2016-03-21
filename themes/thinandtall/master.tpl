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
        <script src="https://ajax.googleapis.com/ajax/libs/jquery/2.2.2/jquery.min.js"></script> 
    </head>
    <body>
        <header>
            <h1 class="title">{{title or 'No title set, fix!'}}</h1>
            <nav>
                % for pge in nav_links:
                <h1><a href="{{pge[0]}}">{{pge[1]}}</a></h1>
                % end
                <h1 id="dropdown"><a>?</a></h1>
                <div id="dropdown-container">
                    % if not is_authenticated:
                    <form action="/login" method="post">
                        <input name="user" placeholder="Username" type="text">
                        <input name="password" placeholder="Password" type="password">
                        <input value="Submit" type="submit">
                    </form>
                    % end
                    % for pge in cog_links:
                    <a href="{{pge[0]}}">{{pge[1]}}</a>
                    % end
                </div>
            </nav>
            <div class="clear"></div>
        </header>
        <div id="pagecontent">
        % include(content)
        </div>
        <script src="/theme/static/dropdown.js"></script> 
    </body>
</html>