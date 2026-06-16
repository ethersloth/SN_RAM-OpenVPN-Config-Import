<?xml version="1.0" encoding="ISO-8859-1"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:output method="xml" indent="yes" omit-xml-declaration="yes" />


<xsl:template match="/GAUCfg/modbus"  > 
	<xsl:element name="modbus" >
		<xsl:attribute name="subsystem">modbus</xsl:attribute><xsl:text>
		</xsl:text>
		<xsl:variable name="modbusLocalName" select="document($clichanges)/modbus/localStation/name" />
		<xsl:element name="enable"><xsl:value-of select="document($clichanges)/modbus/localStation/enable"></xsl:value-of></xsl:element><xsl:text>
        </xsl:text>
		<xsl:element name="localname" ><xsl:value-of select="$modbusLocalName" /></xsl:element><xsl:text>
		</xsl:text>
		<xsl:element name="localStationNum"><xsl:value-of select="document($clichanges)/modbus/localStation/stationNum"></xsl:value-of></xsl:element><xsl:text>
        </xsl:text>
        <xsl:element name="localPort"><xsl:value-of select="document($clichanges)/modbus/localStation/localPort"></xsl:value-of></xsl:element><xsl:text>
        </xsl:text>
        <xsl:element name="AnalogIn"><xsl:value-of select="document($clichanges)/modbus/RegAllocation/AnalogIn"></xsl:value-of></xsl:element><xsl:text>
        </xsl:text>
        <xsl:element name="AnalogOut"><xsl:value-of select="document($clichanges)/modbus/RegAllocation/AnalogOut"></xsl:value-of></xsl:element><xsl:text>
        </xsl:text>
        <xsl:element name="DiscreteIn"><xsl:value-of select="document($clichanges)/modbus/RegAllocation/DiscreteIn"></xsl:value-of></xsl:element><xsl:text>
        </xsl:text>
        <xsl:element name="DiscreteOut"><xsl:value-of select="document($clichanges)/modbus/RegAllocation/DiscreteOut"></xsl:value-of></xsl:element><xsl:text>
        </xsl:text>
        <xsl:element name="FloatIn"><xsl:value-of select="document($clichanges)/modbus/RegAllocation/FloatIn"></xsl:value-of></xsl:element><xsl:text>
        </xsl:text>
        <xsl:element name="FloatOut"><xsl:value-of select="document($clichanges)/modbus/RegAllocation/FloatOut"></xsl:value-of></xsl:element><xsl:text>
        </xsl:text>
        <xsl:element name="LongIn"><xsl:value-of select="document($clichanges)/modbus/RegAllocation/LongIn"></xsl:value-of></xsl:element><xsl:text>
        </xsl:text>
        <xsl:element name="LongOut"><xsl:value-of select="document($clichanges)/modbus/RegAllocation/LongOut"></xsl:value-of></xsl:element><xsl:text>
		</xsl:text>
		<xsl:element name="remoteStations"><xsl:text>
			</xsl:text>
			<xsl:element name="NumberOfremoteStations"><xsl:value-of select="count(document($clichanges)/modbus/remoteStations/remoteStation)" /></xsl:element><xsl:text>
		</xsl:text>
			<xsl:for-each select="document($clichanges)/modbus/remoteStations/remoteStation">
			<xsl:text>	</xsl:text><xsl:element name="remoteStation">
				<xsl:attribute name="record" ><xsl:value-of select="position()" /></xsl:attribute><xsl:text>
				</xsl:text>
				<xsl:element name="name"><xsl:value-of select="name" /></xsl:element><xsl:text>
				</xsl:text>
                <xsl:element name="stationNum"><xsl:value-of select="stationNum" /></xsl:element><xsl:text>
				</xsl:text>
                <xsl:element name="ipaddr"><xsl:value-of select="ipaddr" /></xsl:element><xsl:text>
				</xsl:text>
                <xsl:element name="ipport"><xsl:value-of select="ipport" /></xsl:element><xsl:text>
				</xsl:text>
				<xsl:element name="timeout"><xsl:value-of select="timeout" /></xsl:element><xsl:text>
				</xsl:text>
				<xsl:element name="retries"><xsl:value-of select="retries" /></xsl:element><xsl:text>
				</xsl:text>
				<xsl:element name="stationOnlineType"><xsl:value-of select="stationOnlineType" /></xsl:element><xsl:text>
				</xsl:text>
				<xsl:element name="stationOnlineAddr"><xsl:value-of select="stationOnlineAddr" /></xsl:element><xsl:text>
				</xsl:text>
			</xsl:element><xsl:text>
		</xsl:text></xsl:for-each>
		</xsl:element><xsl:text> 
		</xsl:text>
        	<xsl:element name="serials"><xsl:text>
            		</xsl:text>
            		<xsl:element name="NumberOfserials"><xsl:value-of select="count(document($clichanges)/modbus/serials/serial)" /></xsl:element><xsl:text>
        		</xsl:text>
            		<xsl:for-each select="document($clichanges)/modbus/serials/serial">
                	<xsl:text>	</xsl:text><xsl:element name="serial">
				<xsl:attribute name="record" ><xsl:value-of select="position()" /></xsl:attribute><xsl:text>
				</xsl:text>
					<xsl:element name="device"><xsl:value-of select="device" /></xsl:element><xsl:text>
					</xsl:text>
					<xsl:element name="leadTime"><xsl:value-of select="leadTime" /></xsl:element><xsl:text>
					</xsl:text>
					<xsl:element name="lagTime"><xsl:value-of select="lagTime" /></xsl:element><xsl:text>
					</xsl:text>
					<xsl:element name="baudRate"><xsl:value-of select="baudRate" /></xsl:element><xsl:text>
					</xsl:text>
					<xsl:element name="dataBits"><xsl:value-of select="dataBits" /></xsl:element><xsl:text>
					</xsl:text>
					<xsl:element name="parity"><xsl:value-of select="parity" /></xsl:element><xsl:text>
					</xsl:text>
					<xsl:element name="flowControl"><xsl:value-of select="flowControl" /></xsl:element><xsl:text>
					</xsl:text>
					<xsl:element name="stopBits"><xsl:value-of select="stopBits" /></xsl:element><xsl:text>
					</xsl:text>
					<xsl:element name="protocol"><xsl:value-of select="protocol" /></xsl:element><xsl:text>
					</xsl:text>
					<xsl:element name="floatWordOrder"><xsl:value-of select="floatWordOrder" /></xsl:element><xsl:text>
					</xsl:text>
					<xsl:element name="longWordOrder"><xsl:value-of select="longWordOrder" /></xsl:element><xsl:text>
					</xsl:text>
					<xsl:element name="danielMode"><xsl:value-of select="danielMode" /></xsl:element><xsl:text>
					</xsl:text>
				</xsl:element><xsl:text>
        	</xsl:text></xsl:for-each>
        	</xsl:element><xsl:text> 
        	</xsl:text>
		<xsl:element name="xfers"><xsl:text>
			</xsl:text>
			<xsl:element name="NumberOfxfers"><xsl:value-of select="count(document($clichanges)/modbus/remoteStations/remoteStation/xfer)" /></xsl:element>
		<xsl:variable name="xfers" select="xfers/xfer" />
		<xsl:for-each select="document($clichanges)/modbus/remoteStations/remoteStation/xfer">
		<xsl:text>	
			</xsl:text>
			<xsl:element name="xfer" >
			<xsl:attribute name="record" ><xsl:value-of select="position()" /></xsl:attribute><xsl:text>
				</xsl:text>
				<xsl:variable name="xferNumber"><xsl:value-of select="position()"/></xsl:variable>
                <xsl:element name="localaddrdisp" /><xsl:text>
                </xsl:text>
                <xsl:element name="remoteaddrdisp" /><xsl:text>
                </xsl:text>
                <xsl:element name="localrelAddr"><xsl:value-of select="localAddr + 1"/></xsl:element><xsl:text>
                </xsl:text>
                <xsl:element name="remoterelAddr"><xsl:value-of select="remoteAddr + 1"/></xsl:element><xsl:text>
                </xsl:text>
					<xsl:text>	</xsl:text><xsl:element name="name" >
						<xsl:value-of select="stationName" />
					</xsl:element><xsl:text>
			</xsl:text>
				
				<xsl:for-each select="*[name()!='stationName']">
					<xsl:variable name="name" ><xsl:value-of select="name()" /></xsl:variable>
					<xsl:text>	</xsl:text><xsl:element name="{$name}" >
						<xsl:value-of select="." />
					</xsl:element><xsl:text>
			</xsl:text>
			</xsl:for-each>
		</xsl:element>
		</xsl:for-each><xsl:text>
		</xsl:text>
	</xsl:element><xsl:text>
		</xsl:text>
		<xsl:element name="forwards"><xsl:text>
			</xsl:text>
			<xsl:element name="NumberOfforwards"><xsl:value-of select="count(document($clichanges)/modbus/forwards/forward)" /></xsl:element>
		<xsl:for-each select="document($clichanges)/modbus/forwards/forward">
			<xsl:text>	
			</xsl:text>
			<xsl:element name="forward" >
			<xsl:attribute name="record" ><xsl:value-of select="position()" /></xsl:attribute><xsl:text>
			</xsl:text>
			<xsl:for-each select="*">
				<xsl:variable name="name" ><xsl:value-of select="name()" /></xsl:variable>
				<xsl:text>	</xsl:text><xsl:element name="{$name}" >
					<xsl:value-of select="." />
				</xsl:element><xsl:text>
			</xsl:text>
			</xsl:for-each>
		</xsl:element>
		</xsl:for-each><xsl:text>
		</xsl:text>
	</xsl:element><xsl:text>
	</xsl:text>
	
	
	</xsl:element> 
        	
	
<!-- 
        <serials>
            <NumberOfserials>1</NumberOfserials>
            <serial record="1">
                <device>ttyS1</device>
                <baudRate>9600</baudRate>
                <dataBits>8</dataBits>
                <parity>n</parity>
                <flowControl>n</flowControl>
                <stopBits>1</stopBits>
                <protocol>modbusMasterAscii</protocol>
                <floatWordOrder>LSW</floatWordOrder>
                <longWordOrder>LSW</longWordOrder>
                <danielMode>n</danielMode>
            </serial>
        </serials>
        <xfers>
            <NumberOfxfers>2</NumberOfxfers>
            <xfer record="1">
                <localaddrdisp>0:00000</localaddrdisp>
                <remoteaddrdisp>0:00000</remoteaddrdisp>
                <name>DI1</name>
                <protocol>modbus</protocol>
                <sendMode>rapidFire</sendMode>
                <port>TCP</port>
                <command>READ</command>
                <localType>DI</localType>
                <localAddr>0</localAddr>
                <remoteType>DI</remoteType>
                <remoteAddr>0</remoteAddr>
                <numRegs>16</numRegs>
                <interval>10</interval>
                <scanEnableType />
                <scanEnableAddr />
            </xfer>
            <xfer record="2">
                <localaddrdisp>1:00000</localaddrdisp>
                <remoteaddrdisp>1:00000</remoteaddrdisp>
                <name>DO1</name>
                <protocol>modbus</protocol>
                <sendMode>rapidFire</sendMode>
                <port>TCP</port>
                <command>WRITE</command>
                <localType>DO</localType>
                <localAddr>0</localAddr>
                <remoteType>DO</remoteType>
                <remoteAddr>0</remoteAddr>
                <numRegs>8</numRegs>
                <interval>10</interval>
                <scanEnableType />
                <scanEnableAddr />
            </xfer>
        </xfers>
        <forwards>
            <NumberOfforwards>0</NumberOfforwards>
            <forward>
            	<stationNum>5</stationNum>
            	<dunno>34</dunno>
            	<twest>apple</twest>
            </forward>
            <forward>
            	<stationNum>5</stationNum>
            	<dunno>34</dunno>
            	<twest>apple</twest>
            </forward>
        </forwards> -->
</xsl:template>

<xsl:template match="/GAUCfg">
	<xsl:element name="GAUCfg" >
	<xsl:copy-of select="@*" />
		<xsl:for-each select="*" xml:space="preserve">
	<xsl:apply-templates select="."  /></xsl:for-each><xsl:text>
</xsl:text>
	</xsl:element>
</xsl:template>

<xsl:template match="@*">
	<xsl:copy>
		<xsl:apply-templates select="@*|node()" />
	</xsl:copy>
</xsl:template>

<xsl:template match="node()" >
	<xsl:copy>
		<xsl:apply-templates select="@*|node()" />
	</xsl:copy>
</xsl:template>


</xsl:stylesheet>
