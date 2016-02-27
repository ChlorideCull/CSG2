<!DOCTYPE html>
<html>
    <head>
        <title>{{title or 'No title set, fix!'}}</title>
        <link rel="stylesheet" href="/sass/master.scss">
        % for lnk in link_elements:
        <link rel="{{lnk[0]}}" href="{{lnk[1]}}">
        % end
    </head>
    <body>
        <div id="maincontainer">
            <header>
                <nav>
                    % for pge in nav_links:
                    <a href="{{pge[0]}}">{{pge[1]}}</a>
                    % end
                </nav>
            </header>
            <div id="pagecontent">
% include(content)
            </div>
        </div>
    </body>
</html>