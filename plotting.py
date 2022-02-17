import io, numpy as np, cv2 as cv, plotly.express as px, plotly.graph_objects as go
from plotly.subplots import make_subplots
from PIL import Image

#get a vertical line graph from top to bottom of a 1-D array
def get_line(array1d, render = False):
    fig = px.line(array1d, width = 500, height = 100)
    
    # hide and lock down axes
    fig.update_xaxes(visible=False, fixedrange=True)
    fig.update_yaxes(visible=False, fixedrange=True)
    
    # remove facet/subplot labels
    fig.update_layout(annotations=[], overwrite=True)
    
    #set yaxis range
    fig.update_layout(yaxis_range=[0,8000])
    
    # strip down the rest of the plot
    fig.update_layout(
        showlegend=False,
        plot_bgcolor="white",
        margin=dict(t=0,l=0,b=0,r=0)
    )
    
    # disable the modebar for such a small plot
    fig.show(config=dict(displayModeBar=False))
    
    fig.update_traces(line=dict(color="Black", width=0.7))

    return pfa(fig, render)


#convert Plotly fig to  an array
def pfa(fig, render = False):
    
    #do various byte conversions
    fig_bytes = fig.to_image(format="png")
    buf = io.BytesIO(fig_bytes)
    img = Image.open(buf)
    img = np.asarray(img)
    
    #convert to grayscale, invert colour and rotate so it's vertical & downwards
    img = cv.cvtColor(img, cv.COLOR_RGB2GRAY)
    img = 255-img
    img = np.rot90(img, 3)
    
    if render:
        cv.imshow("",img);cv.waitKey(0);cv.destroyAllWindows()
    else:
        return img

def pfa_generic(fig, render=False):
    #do various byte conversions
    fig_bytes = fig.to_image(format="png")
    buf = io.BytesIO(fig_bytes)
    img = Image.open(buf)
    img = np.asarray(img)
    
    #img = cv.cvtColor(img, cv.COLOR_RGB2GRAY)

    if render:
        cv.imshow("",img);cv.waitKey(0);cv.destroyAllWindows()
    else:
        return img

#FIXME maybe opencv has a function that already does this
def stitch(image, plot):
    
    #resize plot to fit image's height. the dim argument is (width,height)
    plot = cv.resize(plot, (plot.shape[1], image.shape[0]))
    
    return np.concatenate((image,plot),axis=1)


def plot_two(lot, title = None):
    area = [i[0] for i in lot]
    circularity = [i[1] for i in lot]
    slices = list(range(len(lot)))
    
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add traces
    fig.add_trace(
        go.Scatter(x=slices, y=area, name="Area"),
        secondary_y=False,
    )
    
    fig.add_trace(
        go.Scatter(x=slices, y=circularity, name="Circularity"),
        secondary_y=True,
    )
    
    # Add figure title
    fig.update_layout(
        title_text=title,
        font={"size":10}
    )
    
    # Set x-axis title
    fig.update_xaxes(title_text="Slice")
    
    # Set y-axes titles
    fig.update_yaxes(title_text="Area", secondary_y=False)
    fig.update_yaxes(title_text="Circularity", secondary_y=True)
    
    return fig



