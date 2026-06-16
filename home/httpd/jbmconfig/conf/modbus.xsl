<?xml version="1.0" encoding="ISO-8859-1"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:output method="xml" />
<xsl:preserve-space elements="xsl:* xml:*" />

<xsl:template match="/GAUCfg">
	<xsl:apply-templates select="modbus"/>
</xsl:template>

<xsl:template match="node()">
    <xsl:copy>
        <xsl:apply-templates select="@*|node()"/>
    </xsl:copy>
</xsl:template>

<xsl:template match="@*" xml:space="preserve"><xsl:copy xml:space="preserve">
        <xsl:apply-templates xml:space="preserve" select="@*|node()"/>
    </xsl:copy>
</xsl:template>

<xsl:template match="modbus/forwards" >
	<xsl:element name="forwards" >
		<xsl:for-each select="*" xml:space="preserve"><xsl:apply-templates select="."/></xsl:for-each><xsl:text>	</xsl:text>
	</xsl:element>
</xsl:template>

<xsl:template match="modbus/forwards/forward" >
<xsl:text>		</xsl:text>		<xsl:element name="forward" xml:space="preserve">
		<xsl:for-each select="*" xml:space="preserve">	<xsl:apply-templates xml:space="preserve" select="."/>
		</xsl:for-each></xsl:element><xsl:text>
</xsl:text>
</xsl:template>

<xsl:template match="modbus/remoteStations/NumberOfremoteStations" >
	<xsl:element name="NumberOfremoteStations"><xsl:value-of select="count(parent::remoteStations/remoteStation)"/></xsl:element>
</xsl:template>

<xsl:template match="modbus/remoteStations" >
	<xsl:element name="remoteStations" xml:space="preserve">
		<xsl:apply-templates select="*"/>
	</xsl:element>
</xsl:template>


<!-- Build our own, ignore source -->
<xsl:template match="/GAUCfg/modbus/xfers/NumberOfxfers"></xsl:template>

<xsl:template match="modbus/xfers/xfer" ><xsl:text>
			</xsl:text>
			<xsl:element name="xfer" ><xsl:text>
			</xsl:text><xsl:for-each select="*[name() != 'localaddrdisp' and name() != 'remoteaddrdisp' and name() != 'localrelAddr' and name() != 'remoterelAddr']" >
				<xsl:choose><xsl:when test="name()='name'"><xsl:text>	</xsl:text>
					<xsl:element name="stationName" ><xsl:value-of select="."></xsl:value-of></xsl:element>
				</xsl:when><xsl:otherwise><xsl:text>	</xsl:text>
					<xsl:element name="{name()}" ><xsl:value-of select="."></xsl:value-of></xsl:element>
				</xsl:otherwise></xsl:choose><xsl:text>
			</xsl:text>
			</xsl:for-each>
			</xsl:element><xsl:text></xsl:text>
</xsl:template>

<xsl:template match="modbus/remoteStations/remoteStation/*" xml:space="preserve">
	<xsl:apply-templates select="*"/>
</xsl:template>

<xsl:template match="modbus/remoteStations/remoteStation" ><xsl:text>
		</xsl:text>
		<xsl:element name="remoteStation" >
		<xsl:for-each select="*" xml:space="preserve">
			<xsl:copy-of select="."  /></xsl:for-each>
		<xsl:variable name="remoteStationName" select="name" />
			<xsl:text>
			</xsl:text><xsl:element name="NumberOfxfers"><xsl:value-of select="count(/GAUCfg/modbus/xfers/xfer[name=$remoteStationName])" /></xsl:element><xsl:text>	</xsl:text>
		<xsl:apply-templates select="/GAUCfg/modbus/xfers/xfer[name=$remoteStationName]" xml:space="preserve" />
		<xsl:text>	
		</xsl:text>
		</xsl:element>
</xsl:template>

<xsl:template match="modbus/enable">
</xsl:template>

<xsl:template match="modbus/localname">
</xsl:template>

<xsl:template match="modbus/localStationNum">
</xsl:template>

<xsl:template match="modbus/serials" >
	<xsl:element name="serials" ><xsl:text>
		</xsl:text>
		<xsl:apply-templates select="*"></xsl:apply-templates><xsl:text>	</xsl:text></xsl:element><xsl:text>
</xsl:text>
</xsl:template>

<xsl:template match="modbus/serials/serial/device" >
			<xsl:element name="device"><xsl:value-of select="."></xsl:value-of></xsl:element>
</xsl:template>

<xsl:template match="modbus/serials/serial" xml:space="preserve">
		<xsl:element name="serial" ><xsl:attribute name="device" ><xsl:value-of select="device"/></xsl:attribute>
			<xsl:apply-templates select="device"></xsl:apply-templates><xsl:for-each select="*[name()!='device']">
			<xsl:copy-of select="." /></xsl:for-each>
		</xsl:element>
</xsl:template> 

<xsl:template match="modbus/serials/NumberOfserials"  >
		<xsl:element name="NumberOfserials" ><xsl:value-of select="."></xsl:value-of></xsl:element>
</xsl:template>


<xsl:template match="modbus/forwards/NumberOfforwards" xml:space="preserve" >
		<xsl:element name="NumberOfforwards" ><xsl:value-of select="count(parent::*/*[name()='forward'])"></xsl:value-of></xsl:element>
</xsl:template>

<xsl:template match="xfers/xfer/remoteaddrdisp" />

<xsl:template match="xfers/xfer/localaddrdisp" />

<xsl:template match="xfers/xfer/localrelAddr" />

<xsl:template match="xfers/xfer/remoterelAddr" />

<xsl:template match="modbus/*" >

</xsl:template> 

<xsl:template match="modbus" >
<xsl:variable name="subsystem" select="@subsystem" />
<xsl:element name="modbus" xml:space="preserve"><xsl:attribute name="subsytem"><xsl:value-of select="@subsystem"/></xsl:attribute>
	<xsl:apply-templates select="serials" ></xsl:apply-templates>	
	<xsl:element name="localStation" xml:space="preserve">
		<enable><xsl:value-of select="enable"/></enable>
		<name><xsl:value-of select="localname"/></name>
		<stationNum><xsl:value-of select="localStationNum"/></stationNum>
		<localPort><xsl:value-of select="localPort"/></localPort>
	</xsl:element>
	<xsl:element name="RegAllocation" xml:space="preserve">
		<xsl:copy-of select="/GAUCfg/modbus/AnalogIn"/>
		<xsl:copy-of select="/GAUCfg/modbus/AnalogOut"/>
		<xsl:copy-of select="/GAUCfg/modbus/DiscreteIn"/>
		<xsl:copy-of select="/GAUCfg/modbus/DiscreteOut"/>
		<xsl:copy-of select="/GAUCfg/modbus/FloatIn"/>
		<xsl:copy-of select="/GAUCfg/modbus/FloatOut"/>
		<xsl:copy-of select="/GAUCfg/modbus/LongIn"/>
		<xsl:copy-of select="/GAUCfg/modbus/LongOut"/>
	</xsl:element>
	<xsl:choose><xsl:when  test="count(remoteStations/*[name()='remoteStation']) != 0"><xsl:apply-templates select="remoteStations" ></xsl:apply-templates></xsl:when><xsl:otherwise><xsl:element name="remoteStations">
		<xsl:element name="NumberOfremoteStations">0</xsl:element>
	</xsl:element>	</xsl:otherwise></xsl:choose>
	<xsl:choose><xsl:when  test="count(forwards/*[name()='forward']) != 0"><xsl:apply-templates select="forwards" ></xsl:apply-templates></xsl:when><xsl:otherwise><xsl:element name="forwards">
		<xsl:element name="NumberOfforwards">0</xsl:element>
	</xsl:element>	</xsl:otherwise></xsl:choose>
</xsl:element>
</xsl:template>

</xsl:stylesheet>
