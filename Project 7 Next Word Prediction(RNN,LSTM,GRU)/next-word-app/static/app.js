const $ = id => document.getElementById(id);
let outputText = '';
async function checkStatus() {
  try {
    const response = await fetch('/api/status');
    if (!response.ok) throw new Error('Server unavailable');
    const state = await response.json();
    $('status').textContent = state.ready ? 'GRU · Files ready' : 'Model setup needed';
    $('setup').hidden = state.ready;
    $('generate').disabled = !state.ready;
  } catch (error) { $('status').textContent = 'Server unavailable'; $('message').textContent = 'Start python app.py in your terminal, then refresh.'; }
}
document.querySelectorAll('[data-seed]').forEach(button => button.addEventListener('click', () => { $('seed').value = button.dataset.seed; $('seed').focus(); }));
$('generate-form').addEventListener('submit', async event => {
  event.preventDefault();
  $('generate').disabled = true;
  $('generate').textContent = 'Generating…';
  $('message').textContent = 'The first request loads your model and may take a moment.';
  $('details').hidden = true; $('suggestion-area').hidden = true; $('copy').hidden = true;
  $('result').textContent = 'Working on your continuation…'; $('warnings').textContent = '';
  try {
    const response = await fetch('/api/generate', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({text:$('seed').value,count:Number($('count').value)}) });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || 'Prediction failed.');
    outputText = result.text;
    $('result').textContent = outputText;
    $('warnings').textContent = result.warnings.join(' ');
    $('suggestions').replaceChildren();
    result.suggestions.forEach(item => { const chip=document.createElement('span'); chip.className='suggestion'; chip.textContent=item.word; const pct=document.createElement('small'); pct.textContent=(item.probability*100).toFixed(2)+'%'; chip.append(pct); $('suggestions').append(chip); });
    $('steps').replaceChildren();
    result.steps.forEach(item => { const row=document.createElement('tr'); [item.step,item.word,(item.probability*100).toFixed(2)+'%'].forEach(value=>{const cell=document.createElement('td');cell.textContent=value;row.append(cell);});$('steps').append(row); });
    $('details').hidden = false; $('suggestion-area').hidden = false; $('copy').hidden = false;
    $('message').textContent = 'Generated '+result.steps.length+' new words.';
    $('status').textContent = 'GRU · Model loaded';
  } catch(error) { $('result').textContent='Your next thought starts here.'; $('message').textContent=error.message; }
  finally { $('generate').disabled=false; $('generate').textContent='Generate continuation ↗'; }
});
$('copy').addEventListener('click', async()=>{try{await navigator.clipboard.writeText(outputText);$('message').textContent='Copied to clipboard.';}catch{$('message').textContent='Select the generated text and copy it manually.';}});
checkStatus();
