# flowchart using graphviz

```graphviz

digraph g1 {

  graph [splines=false];

  // invisible nodes
  node[fontsize=15, shape = box, width=3, height=0] ;
  i1 [ style="invis"];
  i2 [ style="invis"];
  i3 [ style="invis"];
  i4 [ style="invis"];

  node[fontsize=15, color = black, shape = box, width=3, height=1] ;
  a[color=blue, label="a"];
  b[color=green, label="b"];
  c[color=orange, label="c"]; 
  d[color=red, label="d"] ;       

  {rank=same; a -> b -> c};

  {rankdir = TB;    c -> i1[arrowhead=none];
        i1 -> d[label="  FOR EACH\n\n"]; 
        d -> i2[arrowhead=none];
  };

  {rank=same; i3 -> i2[arrowhead=none] };

  {rankdir = TB; 
    b -> i4[style="invis"];
    i4 -> i3[arrowhead=none];
  };

  {rank=same; i4 -> i1};

}

```

```graphviz
digraph g1 {

  graph [splines=false];

  // invisible nodes
  node[ shape = point, width=0, height=0] ;
  i1 [ style="invis"];
  i2 [ style="invis"];
  i3 [ style="invis"];
  i4 [ style="invis"];

  node[fontsize=15, color = black, shape = box, width=3, height=1] ;
  a[color=blue, label="a"];
  b[color=green, label="b"];
  c[color=orange, label="c"]; 
  d[color=red, label="d"] ;       

  {rank=same; a -> b -> c};

  c -> i1[arrowhead=none];
  i1 -> d[label="  FOR EACH"]; 
  d -> i2[arrowhead=none];

  {rank=same; i3 -> i2[arrowhead=none, minlen = 7 ] };

  b -> i4[style="invis"];
  i4 -> i3[arrowhead=none];

  {rank=same; i4 -> i1};

}
```

```graphviz
digraph G {
  node [fontname = "Handlee"];
  edge [fontname = "Handlee"];

  draw [
    label = "Draw a picture";
    shape = rect;
  ];
  win [
    label = "You win!";
    shape = oval;
  ];
  guess [
    label = "Did they\nguess it?";
    shape = diamond;
  ];
  point [
    label = "Point repeatedly\nto the same picture.";
    shape = rect;
  ];

  draw -> guess;
  win -> guess [ label = "Yes"; dir=back ];
  point -> guess;
  guess -> point [ label = "No" ];
  {
    rank=same;
    guess; point; win;
  }
}
```

```graphviz
digraph G {
  node [fontname = "Handlee"];
  edge [fontname = "Handlee"];

  splines=false;
  
  draw [
    label = "Draw a picture";
    shape = rect;
  ];
  win [
    label = "You win!";
    shape = oval;
  ];
  guess [
    label = "Did they\nguess it?";
    shape = diamond;
  ];
  point [
    label = "Point repeatedly\nto the same picture.";
    shape = rect;
  ];

  draw -> guess;
  win -> guess [ label = "Yes"; dir=back ];
  guess -> point [ label = "No" ];

  {
    rank=same;
    guess; point; win;
  }
  
  {
    rank=same;
    guess2; point2; 
  }
  
  guess2 [
      label = "                     ";
      color= white ;
  ];
  point2 [
      label = "                       ";
      color=white;
  ];
  
  point:s -> point2:n [ arrowhead = none ];
  guess2:n -> point2:n [ arrowhead = none ];
  guess2:n -> guess:s;
}
```
