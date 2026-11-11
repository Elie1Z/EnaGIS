import type {CSSProperties, ReactNode} from "react";
import {AbsoluteFill, CanvasImage, Interactive, staticFile, useVideoConfig} from "remotion";
import "../design";

export const Frame = ({children, dark = false, style}: {
  children: ReactNode;
  dark?: boolean;
  style?: CSSProperties;
}) => (
  <AbsoluteFill style={{
    backgroundColor: dark ? "#032536" : "#F7F6F0",
    color: dark ? "#F7F6F0" : "#032536",
    fontFamily: "Inter",
    overflow: "hidden",
    ...style,
  }}>
    {children}
  </AbsoluteFill>
);

export const SmallBrand = () => {
  const {fps} = useVideoConfig();
  return <CanvasImage name="EnaGIS identity" src={staticFile("brand/enagis-wordmark.png")}
    premountFor={fps} style={{position:"absolute",left:192,top:120,width:380,height:"auto"}}/>;
};

export const Kicker = ({children}: {children: string}) => (
  <Interactive.Div name="Scene label" style={{
    position:"absolute",left:192,top:126,color:"#087A64",fontSize:34,
    fontWeight:650,letterSpacing:5,textTransform:"uppercase",
  }}>{children}</Interactive.Div>
);
