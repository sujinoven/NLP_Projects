{{flutter_js}}
{{flutter_build_config}}
const startup = document.getElementById('startup');
const message = document.getElementById('startup-message');

function startupError(error) {
  console.error('Flutter startup failed:', error);
  if (message) {
    message.textContent = 'The app could not start. Refresh the page and check the Flutter terminal or browser console.';
  }
}

_flutter.loader.load({
  onEntrypointLoaded: async function(engineInitializer) {
    try {
      if (message) message.textContent = 'Preparing the display…';
      const appRunner = await engineInitializer.initializeEngine();
      if (message) message.textContent = 'Opening your workspace…';
      await appRunner.runApp();
      if (startup) startup.remove();
    } catch (error) {
      startupError(error);
    }
  }
}).catch(startupError);
