# Soil Cook

A planner for mixing organic living soil. You tell it your pots, and it works out how many whole bags to buy, what the batch costs, and how much premix to add, with as little left over as possible.

## What it does

- **Plan & shop:** enter pot size and count, aeration rock and mix settings. It picks the smallest number of coco blocks that fills your pots, compares 1–12 blocks side by side, and builds a shopping list with bags, leftover and cost. You can copy the list.
- **Mix:** the base recipe (aeration, moisture, compost, castings, biochar) and the premix amounts for the batch, with mixing and cooking steps.
- **Prices:** every ingredient's bag size, volume and price. Every other section reads from here.
- **Premix cost:** cups and pounds per batch, cost per batch and per gallon, and how many batches each bag lasts.
- **Local stores:** a call sheet for Fredericksburg-area stores (log calls and notes) plus a price comparison that finds the cheapest store per ingredient and checks it against online prices.
- **Guide:** other ingredients, combinations to A/B test with a results log, and notes.

Your edits are saved in your browser on the device you use (local storage). They don't sync between devices.

## Run it

It's a single static file with no build step. Open `index.html` in a browser, or serve the folder:

```sh
python3 -m http.server 8000
```

## Deploy

Hosted on Vercel as a static site, with no build step.

```sh
vercel          # first run: links the folder to a Vercel project and makes a preview
vercel --prod   # deploys to production
```

To deploy automatically on every push, connect the GitHub repo to the Vercel project (`vercel git connect`, or Project → Settings → Git in the Vercel dashboard).

Prices were checked Oct 23–24, 2026, before shipping and tax.
