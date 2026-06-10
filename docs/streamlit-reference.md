\# Streamlit documentation website



> Streamlit is a powerful open-source Python framework that allows data

scientists and AI/ML engineers to build interactive apps (i.e. data apps)

with only a few lines of code.



\## \[Get started](/get-started)



Get started with Streamlit, from installation to your first app.



\### \[Installation](/get-started/installation)



Learn how to install Streamlit with comprehensive guides to use pip, conda, Anaconda Distribution, cloud environments, and command line tools.



\- \[Use Streamlit Playground](/get-started/installation/streamlit-playground)

&#x20; Quick start guide to Streamlit using the Streamlit Playground - no installation required.

\- \[Install via command line](/get-started/installation/command-line)

&#x20; Step-by-step guide to install Streamlit using command line tools and build your first Hello World app.

\- \[Install via Anaconda Distribution](/get-started/installation/anaconda-distribution)

&#x20; Step-by-step guide to install Streamlit using Anaconda Distribution and build your first Hello World app.

\- \[Use GitHub Codespaces](/get-started/installation/community-cloud)

&#x20; Quick start guide to use Community Cloud and GitHub Codespaces for browser-based development without local installation.

\- \[Use Snowflake](/get-started/installation/streamlit-in-snowflake)

&#x20; Quick start guide to use Streamlit in Snowflake for secure development with role-based access control.



\### \[Fundamentals](/get-started/fundamentals)



Learn Streamlit fundamentals with guides on main concepts and features.



\- \[Basic concepts](/get-started/fundamentals/main-concepts)

&#x20; Learn the fundamental concepts of Streamlit including data flow, widgets, layout, and the development workflow for building interactive apps.

\- \[Advanced concepts](/get-started/fundamentals/advanced-concepts)

&#x20; Learn advanced Streamlit concepts including caching with st.cache\_data and st.cache\_resource, session state management, and database connections.

\- \[Additional features](/get-started/fundamentals/additional-features)

&#x20; Explore additional Streamlit features including theming, multipage apps, fragments, custom components, and advanced UI customization options.

\- \[Summary](/get-started/fundamentals/summary)

&#x20; A summary of Streamlit's app model including execution flow, data handling, and state management.



\### \[First steps](/get-started/tutorials)



Build your first Streamlit apps with step-by-step tutorials for creating single-page and multi-page applications.



\- \[Create an app](/get-started/tutorials/create-an-app)

&#x20; Step-by-step tutorial for creating your first Streamlit app.

\- \[Create a multipage app](/get-started/tutorials/create-a-multipage-app)

&#x20; Build your first multipage app.



\## \[Develop](/develop)



Complete development resources for building beautiful, performant web apps with Streamlit including concepts, API reference, tutorials, and quick references.



\### \[Concepts](/develop/concepts)



Explore comprehensive guides to Streamlit development concepts including architecture, app design, testing, configuration, connections, custom components, and multipage applications.



\- \[Architecture and execution](/develop/concepts/architecture)

&#x20; Explore comprehensive guides about Streamlit's architecture and execution model, including app lifecycle, caching, session state, forms, fragments, and widget behavior.

&#x20; - \[Running your app](/develop/concepts/architecture/run-your-app)

&#x20;   Learn how to run Streamlit apps locally, set parameters, configure environment variables, and understand the execution model for development and production.

&#x20; - \[Streamlit's architecture](/develop/concepts/architecture/architecture)

&#x20;   Learn about Streamlit's client-server architecture, WebSocket connections, session management, and deployment considerations.

&#x20; - \[The app chrome](/develop/concepts/architecture/app-chrome)

&#x20;   Learn about Streamlit's app chrome including the status area, toolbar, and configurable app menu with developer options and deployment features.

&#x20; - \[Caching](/develop/concepts/architecture/caching)

&#x20;   Learn about Streamlit's caching mechanisms including st.cache\_data and st.cache\_resource for improving app performance and managing expensive computations.

&#x20; - \[Session State](/develop/concepts/architecture/session-state)

&#x20;   Learn about Session State for sharing variables between reruns, implementing callbacks, and building stateful applications across user sessions.

&#x20; - \[Forms](/develop/concepts/architecture/forms)

&#x20;   Learn how to use Streamlit forms with st.form to batch user input, control app reruns, and create efficient interactive interfaces with submit buttons.

&#x20; - \[Fragments](/develop/concepts/architecture/fragments)

&#x20;   Learn how to use Streamlit fragments to optimize app performance by rerunning portions of code instead of full scripts, improving efficiency for complex applications.

\- \[Architecture and execution/ Widget behavior](/develop/concepts/architecture/widget-behavior)

&#x20; Learn how Streamlit widgets behave across reruns, handle state persistence, manage user interactions, and control widget lifecycle in your applications.

\- \[Multipage apps](/develop/concepts/multipage-apps)

&#x20; Explore comprehensive guides about creating multipage Streamlit apps with navigation, page management, URL routing, and best practices for organizing complex apps.

&#x20; - \[Overview](/develop/concepts/multipage-apps/overview)

&#x20;   Learn about Streamlit's features for creating multipage apps using st.navigation, st.Page, and the pages directory with automatic navigation.

&#x20; - \[Page and navigation](/develop/concepts/multipage-apps/page-and-navigation)

&#x20;   Learn how to use the most flexible and preferred method for defining multipage apps.

&#x20; - \[Pages directory](/develop/concepts/multipage-apps/pages-directory)

&#x20;   Learn how to create multipage Streamlit apps using the simple pages/ directory approach with automatic page recognition and sidebar navigation.

&#x20; - \[Working with widgets](/develop/concepts/multipage-apps/widgets)

&#x20;   Learn how widgets behave across pages in multipage Streamlit apps, including widget state management, IDs, and cross-page interactions.

\- \[App design](/develop/concepts/design)

&#x20; Explore comprehensive guides about app design including layouts and containers, updating elements, button behavior, custom styling, dataframe design, multithreading, and timezone handling.

&#x20; - \[Using layouts and containers](/develop/concepts/design/layouts-and-containers)

&#x20;   Learn how to arrange and organize elements in your Streamlit app using containers, columns, tabs, expanders, flex layouts, and dynamic containers.

&#x20; - \[Update and replace elements](/develop/concepts/design/animate)

&#x20;   Learn how Streamlit commands return objects you can use to update, replace, or clear elements in place. Understand the difference between element objects, container objects, widget values, and widget-mode elements.

&#x20; - \[Button behavior and examples](/develop/concepts/design/buttons)

&#x20;   Learn about Streamlit button behavior, state management, and practical examples using st.button with st.session\_state for interactive applications.

&#x20; - \[Dataframes](/develop/concepts/design/dataframes)

&#x20;   Learn how to display and edit tabular data in Streamlit using st.dataframe and st.data\_editor, including styling, configuration, and interactive features.

&#x20; - \[Multithreading](/develop/concepts/design/multithreading)

&#x20;   Learn about multithreading in Streamlit applications, including limitations, best practices, and techniques for implementing concurrent processes safely.

&#x20; - \[Using custom classes](/develop/concepts/design/custom-classes)

&#x20;   Learn best practices for using custom Python classes, dataclasses, and Enums in Streamlit apps, including handling class redefinition and comparison issues across reruns.

&#x20; - \[Working with timezones](/develop/concepts/design/timezone-handling)

&#x20;   Learn how Streamlit handles timezones, including best practices for displaying datetime information across different user timezones.

\- \[Connections, secrets, and authentication](/develop/concepts/connections)

&#x20; Explore comprehensive guides to connecting Streamlit apps to data sources, managing secrets securely, implementing user authentication, and following security best practices.

&#x20; - \[Connecting to data](/develop/concepts/connections/connecting-to-data)

&#x20;   Learn how to connect Streamlit apps to databases, APIs, and data sources with best practices for data retrieval, caching, and secure data connections.

&#x20; - \[Secrets management](/develop/concepts/connections/secrets-management)

&#x20;   Learn how to manage API keys, credentials, and sensitive data in Streamlit apps using native secrets management and environment variables.

&#x20; - \[User authentication](/develop/concepts/connections/authentication)

&#x20;   Learn how to implement user authentication and personalization in Streamlit apps with admin controls, user information, and personalized experiences across sessions.

&#x20; - \[Security reminders](/develop/concepts/connections/security-reminders)

&#x20;   Learn about essential security practices for Streamlit apps including protecting secrets, secure coding practices, and preventing security vulnerabilities.

\- \[Custom components](/develop/concepts/custom-components)

&#x20; Learn about Streamlit custom components - powerful extensions that unlock capabilities beyond built-in widgets using web technologies.

&#x20; - \[Overview](/develop/concepts/custom-components/overview)

&#x20;   Understand what Streamlit custom components are, when to use them, and compare the v1 and v2 approaches for building interactive extensions.

&#x20; - \[Components v2](/develop/concepts/custom-components/components-v2)

&#x20;   Learn about Streamlit custom components v2 - the next generation framework with enhanced capabilities, bidirectional communication, and simplified development.

&#x20;   - \[Quickstart examples](/develop/concepts/custom-components/components-v2/examples)

&#x20;     Get started quickly with Custom Components v2 through practical examples showing interactive buttons, data exchange, and complete component implementations.

&#x20;     - \[Hello world](/develop/concepts/custom-components/components-v2/examples/hello-world)

&#x20;       A simple static component that displays themed text using Streamlit's CSS custom properties.

&#x20;     - \[Rich data](/develop/concepts/custom-components/components-v2/examples/rich-data)

&#x20;       A component that receives different data types from Python including DataFrames, JSON, and base64 images.

&#x20;     - \[Simple button](/develop/concepts/custom-components/components-v2/examples/simple-button)

&#x20;       An interactive button component that sends trigger values to Python when clicked.

&#x20;     - \[Simple checkbox](/develop/concepts/custom-components/components-v2/examples/simple-checkbox)

&#x20;       A simple checkbox component that sends persistent state values to Python.

&#x20;     - \[Interactive counter](/develop/concepts/custom-components/components-v2/examples/interactive-counter)

&#x20;       A counter component demonstrating state values, trigger values, multiple event handlers, and cleanup functions.

&#x20;     - \[Text input](/develop/concepts/custom-components/components-v2/examples/text-input)

&#x20;       A text input component demonstrating bidirectional communication with programmatic updates from Python.

&#x20;     - \[Danger button](/develop/concepts/custom-components/components-v2/examples/danger-button)

&#x20;       A hold-to-confirm button with frontend validation, visual feedback, and rate limiting.

&#x20;     - \[Radial menu](/develop/concepts/custom-components/components-v2/examples/radial-menu)

&#x20;       A radial selection menu demonstrating state values for persistent selections.

&#x20;   - \[Registration](/develop/concepts/custom-components/components-v2/register)

&#x20;     Learn how to register custom v2 components with HTML, CSS, and JavaScript to define their structure and behavior.

&#x20;   - \[Mounting](/develop/concepts/custom-components/components-v2/mount)

&#x20;     Learn how to mount custom v2 components in your Streamlit app, pass data, handle callbacks, and access component values.

&#x20;   - \[State vs trigger values](/develop/concepts/custom-components/components-v2/state-and-triggers)

&#x20;     Learn the fundamental difference between state and trigger values in Custom Components v2, and when to use each approach for bidirectional communication.

&#x20;   - \[Bidirectional communication](/develop/concepts/custom-components/components-v2/communicate)

&#x20;     Learn how to exchange data between your custom v2 component and Python, including sending data to the frontend and receiving user interactions.

&#x20;   - \[Theming and styling](/develop/concepts/custom-components/components-v2/theming)

&#x20;     Learn how to style Custom Components v2 with Streamlit's theme integration, CSS custom properties, and responsive design patterns.

&#x20;   - \[Package-based components](/develop/concepts/custom-components/components-v2/package-based)

&#x20;     Learn how to build complex Custom Components v2 using package-based development with TypeScript, modern build tools, and external dependencies.

&#x20; - \[Components v1](/develop/concepts/custom-components/components-v1)

&#x20;   Learn how to build and use custom Streamlit components to extend app functionality with third-party Python modules and custom UI elements.

&#x20;   - \[Intro to v1 components](/develop/concepts/custom-components/components-v1/intro)

&#x20;     Learn to develop Streamlit custom components with static and bi-directional communication between Python and JavaScript for extended functionality.

&#x20;   - \[Create a component](/develop/concepts/custom-components/components-v1/create)

&#x20;     Step-by-step guide to creating custom Streamlit components from scratch, including setup, development environment, and component structure.

&#x20;   - \[Limitations](/develop/concepts/custom-components/components-v1/limitations)

&#x20;     Understand the limitations and constraints of Streamlit custom components including iframe restrictions and differences from base Streamlit functionality.

&#x20; - \[Publish a component](/develop/concepts/custom-components/publish)

&#x20;   Learn how to publish Streamlit custom components to PyPI, making them accessible to the Python community and Streamlit users worldwide.

&#x20; - \[Component gallery](https://streamlit.io/components)

\- \[Configuration and theming](/develop/concepts/configuration)

&#x20; Explore comprehensive guides about configuring and customizing Streamlit apps including theming, HTTPS setup, static file serving, and custom styling.

&#x20; - \[Configuration options](/develop/concepts/configuration/options)

&#x20;   Learn about configuration options including config.toml files, environment variables, command-line flags, and runtime configuration management.

&#x20; - \[HTTPS support](/develop/concepts/configuration/https-support)

&#x20;   Configure HTTPS/SSL for Streamlit apps with TLS protocol, SSL termination, reverse proxies, and security best practices for production deployment.

&#x20; - \[Serving static files](/develop/concepts/configuration/serving-static-files)

&#x20;   Learn about static file serving in Streamlit to host and serve media files, assets, and resources that support media embedding and custom content.

&#x20; - \[Customize your theme](/develop/concepts/configuration/theming)

&#x20;   Learn about theming options in config.toml, including color schemes, fonts, and visual styling.

&#x20; - \[Customize colors and borders](/develop/concepts/configuration/theming-customize-colors-and-borders)

&#x20;   Learn how to customize colors, borders, backgrounds, and UI elements in Streamlit apps using theme configuration options and color values.

&#x20; - \[Customize fonts](/develop/concepts/configuration/theming-customize-fonts)

&#x20;   Learn how to configure fonts in Streamlit apps by loading custom font files from URLs or static file serving, with configuration options for different text elements.

\- \[App testing](/develop/concepts/app-testing)

&#x20; Explore comprehensive guides about Streamlit's native app testing framework, including setup, examples, and best practices for CI/CD integration.

&#x20; - \[Get started](/develop/concepts/app-testing/get-started)

&#x20;   Learn the fundamentals of Streamlit app testing with practical examples covering test structure, AppTest initialization, element retrieval, widget manipulation, and result inspection.

&#x20; - \[Beyond the basics](/develop/concepts/app-testing/beyond-the-basics)

&#x20;   Learn Streamlit app testing techniques covering AppTest mutable attributes including secrets, session state, query parameters, and advanced testing patterns.

&#x20; - \[Automate your tests](/develop/concepts/app-testing/automate-tests)

&#x20;   Learn how to integrate Streamlit app testing with Continuous Integration systems like GitHub Actions for automated testing workflows.

&#x20; - \[Example](/develop/concepts/app-testing/examples)

&#x20;   Complete example of testing a Streamlit login page including authentication logic, secrets management, security best practices, and comprehensive test coverage.

&#x20; - \[Cheat sheet](/develop/concepts/app-testing/cheat-sheet)

&#x20;   Quick reference guide for Streamlit app testing with AppTest, covering common testing patterns for text elements, widgets, charts, and interactive components.



\### \[API reference](/develop/api-reference)



Visually explore a gallery of Streamlit's API.



\- \[Write and magic](/develop/api-reference/write-magic)

&#x20; Display information in Streamlit apps using st.write and magic commands - versatile tools for showing text, data, charts, and more with minimal code.

&#x20; - \[st.write](/develop/api-reference/write-magic/st.write)

&#x20;   st.write displays its argument in your app.

&#x20; - \[st.write\_stream](/develop/api-reference/write-magic/st.write\_stream)

&#x20;   st.write\_stream displays a stream or generator in your app using a typewriter effect.

&#x20; - \[magic](/develop/api-reference/write-magic/magic)

&#x20;   Magic commands in Streamlit allow you to display content without explicit commands - just put Markdown strings, data, or charts on their own line.

\- \[Text elements](/develop/api-reference/text)

&#x20; Display and format text in Streamlit apps with titles, headers, markdown, code blocks, captions, badges, and other text formatting components.

&#x20; - \[st.title](/develop/api-reference/text/st.title)

&#x20;   st.title displays text in title formatting.

&#x20; - \[st.header](/develop/api-reference/text/st.header)

&#x20;   st.header displays text in header formatting.

&#x20; - \[st.subheader](/develop/api-reference/text/st.subheader)

&#x20;   st.subheader displays text in subheader formatting.

&#x20; - \[st.markdown](/develop/api-reference/text/st.markdown)

&#x20;   st.markdown displays a string formatted as Markdown.

&#x20; - \[st.badge](/develop/api-reference/text/st.badge)

&#x20;   st.badge displays a colored badge or tag.

&#x20; - \[st.caption](/develop/api-reference/text/st.caption)

&#x20;   st.caption displays text in small font.

&#x20; - \[st.code](/develop/api-reference/text/st.code)

&#x20;   st.code displays a code block with optional syntax highlighting.

&#x20; - \[st.divider](/develop/api-reference/text/st.divider)

&#x20;   st.divider displays a horizontal rule in your app.

&#x20; - \[st.echo](/develop/api-reference/text/st.echo)

&#x20;   st.echo displays some code on the app, and then execute it.

&#x20; - \[st.latex](/develop/api-reference/text/st.latex)

&#x20;   st.latex displays mathematical expressions formatted as LaTeX.

&#x20; - \[st.text](/develop/api-reference/text/st.text)

&#x20;   st.text displays plain text without Markdown formatting.

&#x20; - \[st.help](/develop/api-reference/text/st.help)

&#x20;   st.help displays object's doc string, nicely formatted.

&#x20; - \[st.html](/develop/api-reference/text/st.html)

&#x20;   st.html renders arbitrary HTML strings to your app.

&#x20; - \[st.iframe](/develop/api-reference/text/st.iframe)

&#x20;   st.iframe renders arbitrary HTML, files, or URLs in an iframe.

\- \[Data elements](/develop/api-reference/data)

&#x20; Display and interact with raw data in Streamlit using dataframes, tables, metrics, and data editors for quick, interactive data visualization and manipulation.

&#x20; - \[st.dataframe](/develop/api-reference/data/st.dataframe)

&#x20;   st.dataframe displays a dataframe as an interactive table.

&#x20; - \[st.data\_editor](/develop/api-reference/data/st.data\_editor)

&#x20;   st.data\_editor display a data editor widget that allows you to edit dataframes and many other data structures in a table-like UI.

&#x20; - \[st.column\_config](/develop/api-reference/data/st.column\_config)

&#x20;   Configure data display and interaction in Streamlit dataframes and data editors with st.column\_config - supporting text, numbers, charts, images, URLs, and more.

&#x20;   - \[Column](/develop/api-reference/data/st.column\_config/st.column\_config.column)

&#x20;     st.column\_config.Column configures the display of generic columns with attributes like labels, help text, width, and visibility.

&#x20;   - \[Text column](/develop/api-reference/data/st.column\_config/st.column\_config.textcolumn)

&#x20;     st.column\_config.TextColumn configures text columns for displaying and editing text data with validation and formatting.

&#x20;   - \[Number column](/develop/api-reference/data/st.column\_config/st.column\_config.numbercolumn)

&#x20;     st.column\_config.NumberColumn configures number columns for displaying and editing numerical data with formatting options.

&#x20;   - \[Checkbox column](/develop/api-reference/data/st.column\_config/st.column\_config.checkboxcolumn)

&#x20;     st.column\_config.CheckboxColumn configures checkbox columns for displaying boolean data and interactive true/false selection.

&#x20;   - \[Selectbox column](/develop/api-reference/data/st.column\_config/st.column\_config.selectboxcolumn)

&#x20;     st.column\_config.SelectboxColumn configures selectbox columns for editing categorical columns or columns with a predefined set of possible values.

&#x20;   - \[Multiselect column](/develop/api-reference/data/st.column\_config/st.column\_config.multiselectcolumn)

&#x20;     st.column\_config.MultiselectColumn configures multiselect columns for editing categorical columns or columns with a predefined set of possible values.

&#x20;   - \[Datetime column](/develop/api-reference/data/st.column\_config/st.column\_config.datetimecolumn)

&#x20;     st.column\_config.DatetimeColumn configures datetime columns for displaying and editing datetime values with a formatted text input.

&#x20;   - \[Date column](/develop/api-reference/data/st.column\_config/st.column\_config.datecolumn)

&#x20;     st.column\_config.DateColumn configures date columns for displaying and editing date values with date picker interface.

&#x20;   - \[Time column](/develop/api-reference/data/st.column\_config/st.column\_config.timecolumn)

&#x20;     st.column\_config.TimeColumn configures time columns for displaying and editing time values with time picker interface.

&#x20;   - \[JSON column](/develop/api-reference/data/st.column\_config/st.column\_config.jsoncolumn)

&#x20;     st.column\_config.JsonColumn configures JSON columns for displaying structured JSON data with pretty formatting.

&#x20;   - \[List column](/develop/api-reference/data/st.column\_config/st.column\_config.listcolumn)

&#x20;     st.column\_config.ListColumn configures list columns for displaying and editing arrays, lists, and sequences of data.

&#x20;   - \[Link column](/develop/api-reference/data/st.column\_config/st.column\_config.linkcolumn)

&#x20;     st.column\_config.LinkColumn configures link columns for displaying clickable URLs and hyperlinks within dataframe cells.

&#x20;   - \[Image column](/develop/api-reference/data/st.column\_config/st.column\_config.imagecolumn)

&#x20;     st.column\_config.ImageColumn configures image columns for displaying images directly within dataframe cells from URLs or file paths.

&#x20;   - \[Audio column](/develop/api-reference/data/st.column\_config/st.column\_config.audiocolumn)

&#x20;     st.column\_config.AudioColumn configures audio columns for playing audio directly within dataframe cells from URLs or file paths.

&#x20;   - \[Video column](/develop/api-reference/data/st.column\_config/st.column\_config.videocolumn)

&#x20;     st.column\_config.VideoColumn configures video columns for displaying videos directly within dataframe cells from URLs or file paths.

&#x20;   - \[Area chart column](/develop/api-reference/data/st.column\_config/st.column\_config.areachartcolumn)

&#x20;     st.column\_config.AreaChartColumn configures area chart columns for visualizing time series and numerical data as inline area charts.

&#x20;   - \[Line chart column](/develop/api-reference/data/st.column\_config/st.column\_config.linechartcolumn)

&#x20;     st.column\_config.LineChartColumn configures line chart columns for visualizing time series and numerical data as inline line charts.

&#x20;   - \[Bar chart column](/develop/api-reference/data/st.column\_config/st.column\_config.barchartcolumn)

&#x20;     st.column\_config.BarChartColumn configures bar chart columns for displaying numerical data as inline horizontal bar charts.

&#x20;   - \[Progress column](/develop/api-reference/data/st.column\_config/st.column\_config.progresscolumn)

&#x20;     st.column\_config.ProgressColumn configures progress columns for displaying numerical data as visual progress bars.

&#x20; - \[st.table](/develop/api-reference/data/st.table)

&#x20;   st.table displays a static table.

&#x20; - \[st.metric](/develop/api-reference/data/st.metric)

&#x20;   st.metric displays a metric in big bold font, with an optional indicator of how the metric changed.

&#x20; - \[st.json](/develop/api-reference/data/st.json)

&#x20;   st.json displays object or string as a pretty-printed JSON string.

\- \[Chart elements](/develop/api-reference/charts)

&#x20; Create interactive data visualizations with Streamlit's charting capabilities including simple charts, advanced visualization libraries, and community components.

&#x20; - \[st.area\_chart](/develop/api-reference/charts/st.area\_chart)

&#x20;   st.area\_chart displays an interactive area chart.

&#x20; - \[st.bar\_chart](/develop/api-reference/charts/st.bar\_chart)

&#x20;   st.bar\_chart displays an interactive bar chart.

&#x20; - \[st.line\_chart](/develop/api-reference/charts/st.line\_chart)

&#x20;   st.line\_chart displays an interactive line chart.

&#x20; - \[st.map](/develop/api-reference/charts/st.map)

&#x20;   st.map displays an interactive map with points on it.

&#x20; - \[st.scatter\_chart](/develop/api-reference/charts/st.scatter\_chart)

&#x20;   st.scatter\_chart displays an interactive scatter chart.

&#x20; - \[st.altair\_chart](/develop/api-reference/charts/st.altair\_chart)

&#x20;   st.altair\_chart displays an interactive chart using the Altair library.

&#x20; - \[st.graphviz\_chart](/develop/api-reference/charts/st.graphviz\_chart)

&#x20;   st.graphviz\_chart displays a graph using the dagre-d3 library.

&#x20; - \[st.plotly\_chart](/develop/api-reference/charts/st.plotly\_chart)

&#x20;   st.plotly\_chart displays an interactive Plotly chart.

&#x20; - \[st.pydeck\_chart](/develop/api-reference/charts/st.pydeck\_chart)

&#x20;   st.pydeck\_chart displays an interactive chart using the PyDeck library.

&#x20; - \[st.pyplot](/develop/api-reference/charts/st.pyplot)

&#x20;   st.pyplot displays a matplotlib.pyplot figure.

&#x20; - \[st.vega\_lite\_chart](/develop/api-reference/charts/st.vega\_lite\_chart)

&#x20;   st.vega\_lite\_chart displays an interactive chart using the Vega-Lite library.

\- \[Input widgets](/develop/api-reference/widgets)

&#x20; Add interactivity to Streamlit apps with input widgets including buttons, sliders, text inputs, selectboxes, file uploaders, and more interactive components.

&#x20; - \[st.button](/develop/api-reference/widgets/st.button)

&#x20;   st.button displays a button widget.

&#x20; - \[st.download\_button](/develop/api-reference/widgets/st.download\_button)

&#x20;   st.download\_button displays a download button widget.

&#x20; - \[st.form\_submit\_button](https://docs.streamlit.io/develop/api-reference/execution-flow/st.form\_submit\_button)

&#x20; - \[st.link\_button](/develop/api-reference/widgets/st.link\_button)

&#x20;   st.link\_button displays a button that opens a URL in a new tab.

&#x20; - \[st.menu\_button](/develop/api-reference/widgets/st.menu\_button)

&#x20;   st.menu\_button displays a multi-action drop-down button

&#x20; - \[st.page\_link](/develop/api-reference/widgets/st.page\_link)

&#x20;   st.page\_link displays a link to another page in a multipage app or to an external page.

&#x20; - \[st.checkbox](/develop/api-reference/widgets/st.checkbox)

&#x20;   st.checkbox displays a checkbox widget.

&#x20; - \[st.color\_picker](/develop/api-reference/widgets/st.color\_picker)

&#x20;   st.color\_picker displays a color picker widget.

&#x20; - \[st.feedback](/develop/api-reference/widgets/st.feedback)

&#x20;   st.feedback displays a widget for users to select a sentiment or rating.

&#x20; - \[st.multiselect](/develop/api-reference/widgets/st.multiselect)

&#x20;   st.multiselect displays a drop-down select widget where users can select multiple options.

&#x20; - \[st.pills](/develop/api-reference/widgets/st.pills)

&#x20;   st.pills displays a select widget where options display as pill buttons.

&#x20; - \[st.radio](/develop/api-reference/widgets/st.radio)

&#x20;   st.radio displays a radio button widget.

&#x20; - \[st.segmented\_control](/develop/api-reference/widgets/st.segmented\_control)

&#x20;   st.segmented\_control displays a select widget where options display in a segmented button.

&#x20; - \[st.selectbox](/develop/api-reference/widgets/st.selectbox)

&#x20;   st.selectbox displays a drop-down select widget.

&#x20; - \[st.select\_slider](/develop/api-reference/widgets/st.select\_slider)

&#x20;   st.select\_slider displays a slider widget to select items from a list.

&#x20; - \[st.toggle](/develop/api-reference/widgets/st.toggle)

&#x20;   st.toggle displays a toggle widget.

&#x20; - \[st.number\_input](/develop/api-reference/widgets/st.number\_input)

&#x20;   st.number\_input displays a numeric input widget.

&#x20; - \[st.slider](/develop/api-reference/widgets/st.slider)

&#x20;   st.slider displays a slider widget for numerical values.

&#x20; - \[st.date\_input](/develop/api-reference/widgets/st.date\_input)

&#x20;   st.date\_input displays a date input widget.

&#x20; - \[st.datetime\_input](/develop/api-reference/widgets/st.datetime\_input)

&#x20;   st.datetime\_input displays a datetime input widget.

&#x20; - \[st.time\_input](/develop/api-reference/widgets/st.time\_input)

&#x20;   st.time\_input displays a time input widget.

&#x20; - \[st.chat\_input](https://docs.streamlit.io/develop/api-reference/chat/st.chat\_input)

&#x20; - \[st.text\_area](/develop/api-reference/widgets/st.text\_area)

&#x20;   st.text\_area displays a multi-line text input widget.

&#x20; - \[st.text\_input](/develop/api-reference/widgets/st.text\_input)

&#x20;   st.text\_input displays a single-line text input widget.

&#x20; - \[st.audio\_input](/develop/api-reference/widgets/st.audio\_input)

&#x20;   st.audio\_input displays a widget to upload audio from a microphone.

&#x20; - \[st.camera\_input](/develop/api-reference/widgets/st.camera\_input)

&#x20;   st.camera\_input displays a widget to upload images from a camera.

&#x20; - \[st.data\_editor](https://docs.streamlit.io/develop/api-reference/data/st.data\_editor)

&#x20; - \[st.file\_uploader](/develop/api-reference/widgets/st.file\_uploader)

&#x20;   st.file\_uploader displays a file uploader widget.

\- \[Media elements](/develop/api-reference/media)

&#x20; Embed images, videos, audio files, PDFs, and logos directly into your Streamlit apps with easy-to-use media commands.

&#x20; - \[st.audio](/develop/api-reference/media/st.audio)

&#x20;   st.audio displays an audio player.

&#x20; - \[st.image](/develop/api-reference/media/st.image)

&#x20;   st.image displays an image or list of images.

&#x20; - \[st.logo](/develop/api-reference/media/st.logo)

&#x20;   st.logo displays an image in the upper-left corner of your app and its sidebar.

&#x20; - \[st.pdf](/develop/api-reference/media/st.pdf)

&#x20;   st.pdf displays a PDF viewer.

&#x20; - \[st.video](/develop/api-reference/media/st.video)

&#x20;   st.video displays a video player.

\- \[Layouts and containers](/develop/api-reference/layout)

&#x20; Control how elements are arranged on screen with Streamlit's layout and container components including columns, expanders, sidebars, tabs, and containers.

&#x20; - \[st.columns](/develop/api-reference/layout/st.columns)

&#x20;   st.columns inserts containers laid out as side-by-side columns.

&#x20; - \[st.container](/develop/api-reference/layout/st.container)

&#x20;   st.container inserts a multi-element container that can arrange its contents vertically or horizontally.

&#x20; - \[st.dialog](https://docs.streamlit.io/develop/api-reference/execution-flow/st.dialog)

&#x20; - \[st.empty](/develop/api-reference/layout/st.empty)

&#x20;   st.empty inserts a single-element container.

&#x20; - \[st.expander](/develop/api-reference/layout/st.expander)

&#x20;   st.expander inserts a multi-element container that can be expanded and collapsed.

&#x20; - \[st.form](https://docs.streamlit.io/develop/api-reference/execution-flow/st.form)

&#x20; - \[st.popover](/develop/api-reference/layout/st.popover)

&#x20;   st.popover displays a button that opens a multi-element popover container.

&#x20; - \[st.sidebar](/develop/api-reference/layout/st.sidebar)

&#x20;   st.sidebar displays items in a sidebar.

&#x20; - \[st.bottom](/develop/api-reference/layout/st.bottom)

&#x20;   st.bottom inserts a pinned container at the bottom of the app, perfect for chat inputs, toolbars, and persistent controls.

&#x20; - \[st.space](/develop/api-reference/layout/st.space)

&#x20;   st.space inserts horizontal of vertical spacing to help align elements.

&#x20; - \[st.tabs](/develop/api-reference/layout/st.tabs)

&#x20;   st.tabs displays a set of tabs and inserts associated containers.

\- \[Chat elements](/develop/api-reference/chat)

&#x20; Build conversational apps and chat interfaces using Streamlit's chat elements including st.chat\_input and st.chat\_message for interactive messaging experiences.

&#x20; - \[st.chat\_input](/develop/api-reference/chat/st.chat\_input)

&#x20;   st.chat\_input displays a chat input widget.

&#x20; - \[st.chat\_message](/develop/api-reference/chat/st.chat\_message)

&#x20;   st.chat\_message displays a user or agent icon and inserts a chat message container into the app.

&#x20; - \[st.status](https://docs.streamlit.io/develop/api-reference/status/st.status)

&#x20; - \[st.write\_stream](https://docs.streamlit.io/develop/api-reference/write-magic/st.write\_stream)

\- \[Status elements](/develop/api-reference/status)

&#x20; Display progress bars, status messages, notifications, and celebratory animations in your Streamlit apps.

&#x20; - \[st.success](/develop/api-reference/status/st.success)

&#x20;   st.success displays a success message.

&#x20; - \[st.info](/develop/api-reference/status/st.info)

&#x20;   st.info displays an informational message.

&#x20; - \[st.warning](/develop/api-reference/status/st.warning)

&#x20;   st.warning displays warning message.

&#x20; - \[st.error](/develop/api-reference/status/st.error)

&#x20;   st.error displays an error message.

&#x20; - \[st.exception](/develop/api-reference/status/st.exception)

&#x20;   st.exception displays an exception.

&#x20; - \[st.progress](/develop/api-reference/status/st.progress)

&#x20;   st.progress displays a progress bar.

&#x20; - \[st.spinner](/develop/api-reference/status/st.spinner)

&#x20;   st.spinner temporarily displays a message while executing a block of code.

&#x20; - \[st.status](/develop/api-reference/status/st.status)

&#x20;   st.status inserts a mutable expander element.

&#x20; - \[st.toast](/develop/api-reference/status/st.toast)

&#x20;   st.toast briefly displays a toast message in the upper-right corner.

&#x20; - \[st.balloons](/develop/api-reference/status/st.balloons)

&#x20;   st.balloons displays celebratory balloons!

&#x20; - \[st.snow](/develop/api-reference/status/st.snow)

&#x20;   st.snow displays celebratory snowflakes!

\- \[Third-party components](https://streamlit.io/components)

\- \[Authentication and user info](/develop/api-reference/user)

&#x20; Add user authentication and personalization in your apps with login, logout, and user information access.

&#x20; - \[st.login](/develop/api-reference/user/st.login)

&#x20;   st.login redirects the user to the configured authentication provider to log in.

&#x20; - \[st.logout](/develop/api-reference/user/st.logout)

&#x20;   st.logout removes the user's identity information and starts a clean session.

&#x20; - \[st.user](/develop/api-reference/user/st.user)

&#x20;   st.user returns information about the logged-in user.

\- \[Navigation and pages](/develop/api-reference/navigation)

&#x20; Create multipage Streamlit applications with navigation components for page switching, page management, and programmatic navigation control.

&#x20; - \[st.navigation](/develop/api-reference/navigation/st.navigation)

&#x20;   st.navigation declares the set of available pages available to the user in a multipage app.

&#x20; - \[st.Page](/develop/api-reference/navigation/st.page)

&#x20;   st.Page initializes a StreamlitPage object for multipage apps.

&#x20; - \[st.page\_link](https://docs.streamlit.io/develop/api-reference/widgets/st.page\_link)

&#x20; - \[st.switch\_page](/develop/api-reference/navigation/st.switch\_page)

&#x20;   st.switch\_page programmatically switches the active page.

\- \[Execution flow](/develop/api-reference/execution-flow)

&#x20; Control your app’s execution flow with forms, fragments, dialogs, and more.

&#x20; - \[st.dialog](/develop/api-reference/execution-flow/st.dialog)

&#x20;   st.dialog opens a multi-element modal overlay.

&#x20; - \[st.form](/develop/api-reference/execution-flow/st.form)

&#x20;   st.form creates a form that batches elements together with one or more submit buttons.

&#x20; - \[st.form\_submit\_button](/develop/api-reference/execution-flow/st.form\_submit\_button)

&#x20;   st.form\_submit\_button displays a form submit button.

&#x20; - \[st.fragment](/develop/api-reference/execution-flow/st.fragment)

&#x20;   st.fragment is a decorator that allows a function to rerun independently from the rest of the script.

&#x20; - \[st.rerun](/develop/api-reference/execution-flow/st.rerun)

&#x20;   st.rerun stops the current script run and immediately reruns the script.

&#x20; - \[st.stop](/develop/api-reference/execution-flow/st.stop)

&#x20;   st.stop immediately stops the current script run.

\- \[Caching and state](/develop/api-reference/caching-and-state)

&#x20; Optimize performance and manage state in Streamlit apps with st.cache\_data, st.cache\_resource, session state, and query parameters for efficient applications.

&#x20; - \[st.cache\_data](/develop/api-reference/caching-and-state/st.cache\_data)

&#x20;   st.cache\_data is used to cache functions that return data (e.g. dataframe transforms, database queries, ML inference).

&#x20; - \[st.cache\_resource](/develop/api-reference/caching-and-state/st.cache\_resource)

&#x20;   st.cache\_resource is used to cache functions that return shared, global resources (e.g. database connections, ML models).

&#x20; - \[st.session\_state](/develop/api-reference/caching-and-state/st.session\_state)

&#x20;   st.session\_state is a way to share variables between reruns, for each user session.

&#x20; - \[st.context](/develop/api-reference/caching-and-state/st.context)

&#x20;   st.context displays a read-only dict of cookies and headers.

&#x20; - \[st.query\_params](/develop/api-reference/caching-and-state/st.query\_params)

&#x20;   st.query\_params reads and manipulates query parameters in the browser's URL bar.

\- \[Connections and secrets](/develop/api-reference/connections)

&#x20; Connect to data sources and databases in Streamlit using st.connection, built-in connections, and secure secrets management for seamless data integration.

&#x20; - \[st.secrets](/develop/api-reference/connections/st.secrets)

&#x20;   st.secrets provides a dictionary-like interface to access secrets stored in a secrets.toml file for credential management.

&#x20; - \[secrets.toml](/develop/api-reference/connections/secrets.toml)

&#x20;   secrets.toml is a TOML file for storing secrets, API keys, and credentials for your Streamlit app.

&#x20; - \[st.connection](/develop/api-reference/connections/st.connection)

&#x20;   st.connection creates a connection to a data source or API for accessing external data in your Streamlit app.

&#x20; - \[SnowflakeConnection](/develop/api-reference/connections/st.connections.snowflakeconnection)

&#x20;   st.connections.SnowflakeConnection provides a connection to Snowflake data warehouse for querying and data operations.

&#x20; - \[SQLConnection](/develop/api-reference/connections/st.connections.sqlconnection)

&#x20;   st.connections.SQLConnection provides a connection to SQL databases using SQLAlchemy for querying relational data.

&#x20; - \[BaseConnection](/develop/api-reference/connections/st.connections.baseconnection)

&#x20;   st.connections.BaseConnection is the base class for creating custom connections to data sources and APIs.

&#x20; - \[SnowparkConnection](/develop/api-reference/connections/st.connections.snowparkconnection)

&#x20;   st.connections.SnowparkConnection provides a connection to Snowflake using Snowpark (deprecated, use SnowflakeConnection).

\- \[Custom components](/develop/api-reference/custom-components)

&#x20; Use Streamlit's custom components to create and integrate custom UI elements in your app.

&#x20; - \[component](/develop/api-reference/custom-components/st.components.v2.component)

&#x20;   st.components.v2.component registers a v2 custom component, enabling seamless integration of custom UI elements in Streamlit applications.

&#x20; - \[ComponentRenderer](/develop/api-reference/custom-components/st.components.v2.types.componentrenderer)

&#x20;   Python interface for mounting Streamlit v2 custom components, enabling seamless data exchange with custom UI.

&#x20; - \[component-v2-lib](/develop/api-reference/custom-components/component-v2-lib)

&#x20;   Import TypeScript type aliases from an npm-published package.

&#x20; - \[FrontendRenderer](/develop/api-reference/custom-components/component-v2-lib-frontendrenderer)

&#x20;   TypeScript type alias for custom components v2 frontend functions, enabling streamlined component development with type safety and modern JavaScript frameworks.

&#x20; - \[FrontendRendererArgs](/develop/api-reference/custom-components/component-v2-lib-frontendrendererargs)

&#x20;   TypeScript type alias for custom components v2 arguments, providing type-safe access to component properties, state management, and trigger functions for frontend interactions.

&#x20; - \[FrontendState](/develop/api-reference/custom-components/component-v2-lib-frontendstate)

&#x20;   TypeScript type alias for custom components v2 state management, enabling type-safe state persistence and data flow between component renders and user interactions.

&#x20; - \[CleanupFunction](/develop/api-reference/custom-components/component-v2-lib-cleanupfunction)

&#x20;   TypeScript type alias for custom components v2 state management, enabling type-safe state persistence and data flow between component renders and user interactions.

&#x20; - \[declare\_component](/develop/api-reference/custom-components/st.components.v1.declare\_component)

&#x20;   st.components.v1.declare\_component creates and registers a custom component for use in your Streamlit app.

&#x20; - \[html](/develop/api-reference/custom-components/st.components.v1.html)

&#x20;   st.components.v1.html displays an HTML string in an iframe within your Streamlit app.

&#x20; - \[iframe](/develop/api-reference/custom-components/st.components.v1.iframe)

&#x20;   st.components.v1.iframe embeds web content in an iframe.

\- \[Configuration](/develop/api-reference/configuration)

&#x20; Configure Streamlit apps with config.toml files, page settings, and runtime configuration management for customized app behavior and appearance.

&#x20; - \[config.toml](/develop/api-reference/configuration/config.toml)

&#x20;   Complete reference guide for Streamlit's config.toml configuration file, including all available sections and options for customizing your Streamlit application settings.

&#x20; - \[st.get\_option](/develop/api-reference/configuration/st.get\_option)

&#x20;   st.get\_option retrieves a single configuration option.

&#x20; - \[st.set\_option](/develop/api-reference/configuration/st.set\_option)

&#x20;   st.set\_option updates a single configuration option (from a small list of options that can be updated at runtime).

&#x20; - \[st.set\_page\_config](/develop/api-reference/configuration/st.set\_page\_config)

&#x20;   st.set\_page\_config configures the default settings of the page.

\- \[App testing](/develop/api-reference/app-testing)

&#x20; Run headless tests on your Streamlit app with a built-in testing framework to simulate user input.

&#x20; - \[AppTest](/develop/api-reference/app-testing/st.testing.v1.apptest)

&#x20;   The AppTest class simulates Streamlit apps in automated tests and provides methods to manipulate and inspect app contents programmatically.

&#x20; - \[element\_tree](/develop/api-reference/app-testing/testing-element-classes)

&#x20;   Testing element classes include Block, Element, ChatMessage, Column, and Tab for accessing and inspecting Streamlit app components in tests.

\- \[Command line](/develop/api-reference/cli)

&#x20; Run Streamlit apps and manage configuration using the command-line interface for app execution, cache management, and system diagnostics.

&#x20; - \[streamlit cache](/develop/api-reference/cli/cache)

&#x20;   streamlit cache clear removes persisted files from the on-disk Streamlit cache.

&#x20; - \[streamlit config](/develop/api-reference/cli/config)

&#x20;   streamlit config show displays all available configuration options with descriptions and values.

&#x20; - \[streamlit docs](/develop/api-reference/cli/docs)

&#x20;   streamlit docs opens the Streamlit documentation in your default browser.

&#x20; - \[streamlit hello](/develop/api-reference/cli/hello)

&#x20;   streamlit hello runs an example Streamlit app to verify installation and demonstrate features.

&#x20; - \[streamlit help](/develop/api-reference/cli/help)

&#x20;   streamlit help displays all available CLI commands and their usage information.

&#x20; - \[streamlit init](/develop/api-reference/cli/init)

&#x20;   streamlit init creates the files for a new Streamlit app project including requirements.txt and streamlit\_app.py.

&#x20; - \[streamlit run](/develop/api-reference/cli/run)

&#x20;   streamlit run starts your Streamlit app with optional configuration and script arguments.

&#x20; - \[streamlit version](/develop/api-reference/cli/version)

&#x20;   streamlit version prints Streamlit's version number.



\### \[Tutorials](/develop/tutorials)



Explore step-by-step tutorials for building Streamlit apps including authentication, database connections, data visualization, and advanced features.



\- \[Authentication and personalization](/develop/tutorials/authentication)

&#x20; Learn to implement user authentication in Streamlit apps using OpenID Connect (OIDC) with providers like Google and Microsoft for personalized experiences.

&#x20; - \[Google Auth Platform](/develop/tutorials/authentication/google)

&#x20;   Learn how to authenticate users with Google's OpenID Connect (OIDC) service

&#x20; - \[Microsoft Entra](/develop/tutorials/authentication/microsoft)

&#x20;   Learn how to authenticate users with Microsoft Entra and Microsoft Identity Platform for work, school, and personal accounts in Streamlit apps.

\- \[Chat and LLM apps](/develop/tutorials/chat-and-llm-apps)

&#x20; Learn to build LLM applications with Streamlit including conversational apps, chat interfaces, response feedback, and response revision features.

&#x20; - \[Build a basic LLM chat app](/develop/tutorials/chat-and-llm-apps/build-conversational-apps)

&#x20;   Learn to build conversational LLM applications with Streamlit using chat elements, session state, and Python to create ChatGPT-like experiences.

&#x20; - \[Build an LLM app using LangChain](/develop/tutorials/chat-and-llm-apps/llm-quickstart)

&#x20;   Learn to build an LLM-powered Streamlit app using LangChain and OpenAI, with step-by-step instructions and a deployment guide.

&#x20; - \[Get chat response feedback](/develop/tutorials/chat-and-llm-apps/chat-response-feedback)

&#x20;   Learn to collect user feedback on LLM responses in Streamlit chat apps using st.feedback widget for sentiment collection and response improvement.

&#x20; - \[Validate and edit chat responses](/develop/tutorials/chat-and-llm-apps/validate-and-edit-chat-responses)

&#x20;   Learn to build a Streamlit chat app that lets users validate, correct, and improve LLM chat responses with multi-stage response editing workflows.

\- \[Configuration and theming](/develop/tutorials/configuration-and-theming)

&#x20; Learn to customize Streamlit app themes and configurations including external fonts, static fonts, variable fonts, and visual styling options.

&#x20; - \[Use external font files](/develop/tutorials/configuration-and-theming/external-fonts)

&#x20;   Learn how to use externally hosted fonts and font fallbacks to customize typography in Streamlit apps with variable font files and external resources.

&#x20; - \[Use static font files](/develop/tutorials/configuration-and-theming/static-fonts)

&#x20;   Learn how to use static font files to customize typography in Streamlit apps with self-hosted font files and multiple font weight configurations.

&#x20; - \[Use variable font files](/develop/tutorials/configuration-and-theming/variable-fonts)

&#x20;   Learn how to use variable font files to customize typography in Streamlit apps with self-hosted font files and advanced font configuration options.

\- \[Connect to data sources](/develop/tutorials/databases)

&#x20; Step-by-step tutorials for connecting Streamlit apps to databases and APIs including SQL databases, cloud storage, and popular services.

&#x20; - \[AWS S3](/develop/tutorials/databases/aws-s3)

&#x20;   Learn how to connect to AWS S3 from your Streamlit apps using FilesConnection, s3fs library, and secrets management.

&#x20; - \[BigQuery](/develop/tutorials/databases/bigquery)

&#x20;   Learn how to connect Streamlit apps to Google BigQuery for querying large datasets using service account authentication and st.connection.

&#x20; - \[Firestore](https://blog.streamlit.io/streamlit-firestore/)

&#x20; - \[Google Cloud Storage](/develop/tutorials/databases/gcs)

&#x20;   Learn how to access and manage files on Google Cloud Storage from Streamlit apps using FilesConnection, gcsfs library, and secrets management.

&#x20; - \[Microsoft SQL Server](/develop/tutorials/databases/mssql)

&#x20;   Learn how to connect Streamlit apps to remote Microsoft SQL Server databases using pyodbc library and secrets management for enterprise SQL access.

&#x20; - \[MongoDB](/develop/tutorials/databases/mongodb)

&#x20;   Learn how to connect Streamlit apps to remote MongoDB databases using PyMongo library and secrets management for NoSQL document databases.

&#x20; - \[MySQL](/develop/tutorials/databases/mysql)

&#x20;   Learn how to connect Streamlit apps to remote MySQL databases using st.connection and secrets management for SQL queries and data access.

&#x20; - \[Neon](/develop/tutorials/databases/neon)

&#x20;   Learn how to connect Streamlit apps to Neon serverless PostgreSQL databases with instant branching, automatic scaling, and managed hosting.

&#x20; - \[PostgreSQL](/develop/tutorials/databases/postgresql)

&#x20;   Learn how to connect Streamlit apps to remote PostgreSQL databases using st.connection and secrets management for database queries.

&#x20; - \[Private Google Sheet](/develop/tutorials/databases/private-gsheet)

&#x20;   Learn how to connect Streamlit apps to private Google Sheets using st.connection, GSheetsConnection, service accounts, and secrets management.

&#x20; - \[Public Google Sheet](/develop/tutorials/databases/public-gsheet)

&#x20;   Learn how to connect Streamlit apps to public Google Sheets for data access using st.connection, GSheetsConnection, and secrets management.

&#x20; - \[Snowflake](/develop/tutorials/databases/snowflake)

&#x20;   Learn how to connect Streamlit apps to Snowflake databases using st.connection, Snowpark library, and secrets management for cloud data warehouse access.

&#x20; - \[Supabase](/develop/tutorials/databases/supabase)

&#x20;   Learn how to connect Streamlit apps to Supabase (open source Firebase alternative) using st.connection, Supabase Connector, and PostgreSQL backend.

&#x20; - \[Tableau](/develop/tutorials/databases/tableau)

&#x20;   Learn how to connect Streamlit apps to Tableau for accessing data and visualizations using tableauserverclient library and secrets management.

&#x20; - \[TiDB](/develop/tutorials/databases/tidb)

&#x20;   Learn how to connect Streamlit apps to TiDB distributed SQL databases using st.connection and secrets management for cloud-native database access.

&#x20; - \[TigerGraph](/develop/tutorials/databases/tigergraph)

&#x20;   Learn how to connect Streamlit apps to TigerGraph graph databases using pyTigerGraph library and secrets management for graph analytics.

\- \[Elements](/develop/tutorials/elements)

&#x20; Tutorials for working with Streamlit elements including charts, dataframes, selections, and interactive components for rich user interfaces.

&#x20; - \[Annotate an Altair chart](/develop/tutorials/elements/annotate-an-altair-chart)

&#x20;   Learn how to annotate Altair charts in Streamlit with text, images, and emojis using layered charts for enhanced data visualization.

&#x20; - \[Get dataframe row-selections](/develop/tutorials/elements/dataframe-row-selections)

&#x20;   Learn how to get row selections from users in Streamlit dataframes using st.dataframe selection features for interactive data exploration.

\- \[Execution flow](/develop/tutorials/execution-flow)

&#x20; Master Streamlit's execution model with tutorials on fragments, reruns, and execution control for optimal app performance and user experience.

&#x20; - \[Rerun your app from a fragment](/develop/tutorials/execution-flow/trigger-a-full-script-rerun-from-a-fragment)

&#x20;   Learn how to trigger a full script rerun from within a Streamlit fragment using st.rerun for advanced execution flow control and state management.

&#x20; - \[Create a multiple-container fragment](/develop/tutorials/execution-flow/create-a-multiple-container-fragment)

&#x20;   Learn how to create Streamlit fragments that span multiple containers using st.empty() to prevent element accumulation during fragment reruns.

&#x20; - \[Start and stop a streaming fragment](/develop/tutorials/execution-flow/start-and-stop-fragment-auto-reruns)

&#x20;   Learn how to create streaming fragments with time intervals, and programmatically start and stop auto-reruns for live data monitoring and streaming applications.

\- \[Build custom components](/develop/tutorials/custom-components)

&#x20; Step-by-step tutorials for building Streamlit custom components with the official component template.

&#x20; - \[Create a component with Pure TypeScript](/develop/tutorials/custom-components/template-typescript)

&#x20;   Build a package-based Streamlit custom component using the official template with Pure TypeScript and Vite.

&#x20; - \[Create a component with React + TypeScript](/develop/tutorials/custom-components/template-react)

&#x20;   Build a package-based Streamlit custom component using the official template with React, TypeScript, and Vite.

\- \[Multipage apps](/develop/tutorials/multipage)

&#x20; Learn to build multipage Streamlit applications with custom navigation, dynamic navigation, and advanced page management techniques.

&#x20; - \[Dynamic navigation](/develop/tutorials/multipage/dynamic-navigation)

&#x20;   Learn how to create a dynamic, conditional navigation menu in your multipage app.



\### \[Quick reference](/develop/quick-reference)



Access quick references including API cheat sheets, prerelease features, and comprehensive release notes for Streamlit development.



\- \[Cheat sheet](/develop/quick-reference/cheat-sheet)

&#x20; Comprehensive Streamlit API cheat sheet with all widgets, layout elements, data display, and utility functions for quick reference during development.

\- \[Release notes](/develop/quick-reference/release-notes)

&#x20; A changelog of highlights and fixes for the latest version of Streamlit.

&#x20; - \[2026](/develop/quick-reference/release-notes/2026)

&#x20;   A changelog of highlights and fixes for each version of Streamlit released in 2026.

&#x20; - \[2025](/develop/quick-reference/release-notes/2025)

&#x20;   A changelog of highlights and fixes for each version of Streamlit released in 2025.

&#x20; - \[2024](/develop/quick-reference/release-notes/2024)

&#x20;   A changelog of highlights and fixes for each version of Streamlit released in 2024.

&#x20; - \[2023](/develop/quick-reference/release-notes/2023)

&#x20;   A changelog of highlights and fixes for each version of Streamlit released in 2023.

&#x20; - \[2022](/develop/quick-reference/release-notes/2022)

&#x20;   A changelog of highlights and fixes for each version of Streamlit released in 2022.

&#x20; - \[2021](/develop/quick-reference/release-notes/2021)

&#x20;   A changelog of highlights and fixes for each version of Streamlit released in 2021.

&#x20; - \[2020](/develop/quick-reference/release-notes/2020)

&#x20;   A changelog of highlights and fixes for each version of Streamlit released in 2020.

&#x20; - \[2019](/develop/quick-reference/release-notes/2019)

&#x20;   A changelog of highlights and fixes for each version of Streamlit released in 2019.

\- \[Pre-release features](/develop/quick-reference/prerelease)

&#x20; Explore Streamlit's experimental and beta features before they become stable, including bleeding-edge functionality and upcoming enhancements.



\### \[Quick reference/ Roadmap](https://roadmap.streamlit.app)



\## \[Deploy](/deploy)



Deploy your Streamlit apps to various platforms including Community Cloud, Snowflake, and other cloud providers with comprehensive guides.



\### \[Concepts](/deploy/concepts)



Learn fundamental deployment concepts including dependencies, secrets management, and app startup for Streamlit applications.



\- \[Dependencies](/deploy/concepts/dependencies)

&#x20; Learn how to manage Python dependencies, requirements.txt files, and package installation when deploying Streamlit apps to cloud platforms.

\- \[Secrets](/deploy/concepts/secrets)

&#x20; Learn best practices for managing secrets, credentials, and API keys securely when deploying Streamlit apps to production environments.



\### \[Streamlit Community Cloud](/deploy/streamlit-community-cloud)



Deploy and manage Streamlit apps for free with Community Cloud - connect to GitHub, deploy in minutes, and share with the world.



\- \[Get started](/deploy/streamlit-community-cloud/get-started)

&#x20; Get started with Streamlit Community Cloud - create your account, connect GitHub, and deploy your first app with step-by-step guides.

&#x20; - \[Quickstart](/deploy/streamlit-community-cloud/get-started/quickstart)

&#x20;   Quick start guide to create your Community Cloud account, deploy a sample app, and start editing with GitHub Codespaces in minutes.

&#x20; - \[Create your account](/deploy/streamlit-community-cloud/get-started/create-your-account)

&#x20;   Learn how to create your Streamlit Community Cloud account using email, Google, or GitHub authentication methods.

&#x20; - \[Connect your GitHub account](/deploy/streamlit-community-cloud/get-started/connect-your-github-account)

&#x20;   Connect your GitHub account to Community Cloud to deploy apps from public and private repositories with proper permissions.

&#x20; - \[Explore your workspace](/deploy/streamlit-community-cloud/get-started/explore-your-workspace)

&#x20;   Learn how to navigate your Community Cloud workspace, switch between workspaces, and manage your apps and profile.

&#x20; - \[Deploy from a template](/deploy/streamlit-community-cloud/get-started/deploy-from-a-template)

&#x20;   Learn how to deploy a Streamlit app from a template using Community Cloud's template picker with GitHub Codespaces integration.

&#x20; - \[Fork and edit a public app](/deploy/streamlit-community-cloud/get-started/fork-and-edit-a-public-app)

&#x20;   Learn how to fork and edit public Streamlit apps from Community Cloud with GitHub Codespaces for immediate development.

&#x20; - \[Trust and security](/deploy/streamlit-community-cloud/get-started/trust-and-security)

&#x20;   Learn about Streamlit Community Cloud's security model including authentication, data protection, encryption, and compliance measures.

\- \[Deploy your app](/deploy/streamlit-community-cloud/deploy-your-app)

&#x20; Complete guide to preparing and deploying your Streamlit app on Community Cloud with file organization, dependencies, and secrets management.

&#x20; - \[File organization](/deploy/streamlit-community-cloud/deploy-your-app/file-organization)

&#x20;   Learn how to organize your files, dependencies, and configuration for successful Community Cloud deployment including subdirectories and multiple apps.

&#x20; - \[App dependencies](/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies)

&#x20;   Learn how to manage Python and external dependencies for your Community Cloud app using requirements.txt, packages.txt, and other package managers.

&#x20; - \[Secrets management](/deploy/streamlit-community-cloud/deploy-your-app/secrets-management)

&#x20;   Learn how to securely manage secrets, credentials, and API keys for your Community Cloud app using the secrets management interface.

&#x20; - \[Deploy!](/deploy/streamlit-community-cloud/deploy-your-app/deploy)

&#x20;   Step-by-step guide to deploy your Streamlit app on Community Cloud including repository selection, configuration, and deployment process.

\- \[Manage your app](/deploy/streamlit-community-cloud/manage-your-app)

&#x20; Learn how to manage your deployed Streamlit apps including editing, analytics, settings, and resource optimization on Community Cloud.

&#x20; - \[App analytics](/deploy/streamlit-community-cloud/manage-your-app/app-analytics)

&#x20;   Learn how to view and analyze your Streamlit app's viewership data including total viewers, unique visitors, and privacy considerations.

&#x20; - \[App settings](/deploy/streamlit-community-cloud/manage-your-app/app-settings)

&#x20;   Learn how to configure your Streamlit app settings including URL customization, sharing permissions, and secrets management.

&#x20; - \[Delete your app](/deploy/streamlit-community-cloud/manage-your-app/delete-your-app)

&#x20;   Learn how to delete your Streamlit app from Community Cloud and understand when deletion might be necessary.

&#x20; - \[Edit your app](/deploy/streamlit-community-cloud/manage-your-app/edit-your-app)

&#x20;   Learn how to edit your deployed Streamlit app using GitHub Codespaces or any development environment with automatic deployment updates.

&#x20; - \[Favorite your app](/deploy/streamlit-community-cloud/manage-your-app/favorite-your-app)

&#x20;   Learn how to favorite and unfavorite your Streamlit apps in Community Cloud to quickly access them from your workspace.

&#x20; - \[Reboot your app](/deploy/streamlit-community-cloud/manage-your-app/reboot-your-app)

&#x20;   Learn how to reboot your Streamlit app on Community Cloud to clear memory, force fresh builds, and resolve issues.

&#x20; - \[Rename your app in GitHub](/deploy/streamlit-community-cloud/manage-your-app/rename-your-app)

&#x20;   Learn how to safely rename your GitHub repository or change app coordinates without losing access to your Streamlit app.

&#x20; - \[Upgrade Python](/deploy/streamlit-community-cloud/manage-your-app/upgrade-python)

&#x20;   Learn how to upgrade your Streamlit app's Python version on Community Cloud by deleting and redeploying with advanced settings.

&#x20; - \[Upgrade Streamlit](/deploy/streamlit-community-cloud/manage-your-app/upgrade-streamlit)

&#x20;   Learn how to upgrade your Streamlit library version on Community Cloud using dependency files or rebooting your app.

\- \[Share your app](/deploy/streamlit-community-cloud/share-your-app)

&#x20; Learn how to share your deployed Streamlit app publicly or privately, invite viewers, and add GitHub badges for better discoverability.

&#x20; - \[Embed your app](/deploy/streamlit-community-cloud/share-your-app/embed-your-app)

&#x20;   Learn how to embed your Streamlit app in websites, blogs, and platforms using iframe and oEmbed methods with customizable options.

&#x20; - \[Search indexability](/deploy/streamlit-community-cloud/share-your-app/indexability)

&#x20;   Learn how to optimize your Streamlit app for search engines with custom subdomains, descriptive titles, and meta descriptions.

&#x20; - \[Share previews](/deploy/streamlit-community-cloud/share-your-app/share-previews)

&#x20;   Learn how to create compelling share previews for social media with custom titles and descriptions for your Streamlit app.

\- \[Manage your account](/deploy/streamlit-community-cloud/manage-your-account)

&#x20; Manage your Streamlit Community Cloud account including email updates, GitHub connections, and account deletion options.

&#x20; - \[Sign in and sign out](/deploy/streamlit-community-cloud/manage-your-account/sign-in-sign-out)

&#x20;   Learn how to sign in to and sign out of Streamlit Community Cloud using Google, GitHub, or email authentication methods.

&#x20; - \[Workspace settings](/deploy/streamlit-community-cloud/manage-your-account/workspace-settings)

&#x20;   Learn how to access and manage your Streamlit Community Cloud workspace settings including linked accounts, limits, and support resources.

&#x20; - \[Manage your GitHub connection](/deploy/streamlit-community-cloud/manage-your-account/manage-your-github-connection)

&#x20;   Learn how to manage your GitHub connection to Community Cloud including adding organization access, revoking permissions, and handling account changes.

&#x20; - \[Update your email](/deploy/streamlit-community-cloud/manage-your-account/update-your-email)

&#x20;   Learn how to update your email address on Streamlit Community Cloud using account merging or GitHub account changes.

&#x20; - \[Delete your account](/deploy/streamlit-community-cloud/manage-your-account/delete-your-account)

&#x20;   Learn how to permanently delete your Streamlit Community Cloud account and all associated apps and data.

\- \[Status and limitations](/deploy/streamlit-community-cloud/status)

&#x20; Learn about Community Cloud status, limitations, GitHub OAuth scope, Python environments, configuration overrides, and IP addresses.



\### \[Snowflake](/deploy/snowflake)



Deploy Streamlit apps in Snowflake for enterprise-grade security and data integration with native apps and container services.



\### \[Other platforms](/deploy/tutorials)



Step-by-step deployment guides for various cloud platforms including Community Cloud, Docker, and Kubernetes.



\- \[Docker](/deploy/tutorials/docker)

&#x20; Learn how to containerize and deploy your Streamlit app using Docker with step-by-step instructions for corporate networks and cloud deployment.

\- \[Kubernetes](/deploy/tutorials/kubernetes)

&#x20; Learn how to deploy your Streamlit app using Kubernetes with Google Container Registry, OAuth authentication, and TLS support.



\## \[Knowledge base](/knowledge-base)



Explore troubleshooting guides for common problems.



\### \[FAQ](/knowledge-base/using-streamlit)



Explore answers to frequently asked questions about developing a Streamlit app.



\### \[Installing dependencies](/knowledge-base/dependencies)



Explore common dependency and environment problems, and see possible solutions.



\### \[Deployment issues](/knowledge-base/deploy)



Explore common deployment problems and solutions.

